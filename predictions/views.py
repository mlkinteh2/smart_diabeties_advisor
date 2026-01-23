import os
import numpy as np
import joblib
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Prediction, PredictionFeature
from accounts.models import Patient, Doctor
from .utils import load_models, calculate_risk_level
from recommendations.engine import generate_recommendation


def parse_float(val):
    """Safely parse a float value, returning None if invalid or empty."""
    if val is None or val == "":
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


@login_required
def create_prediction(request, patient_id):
    """Doctor creates a new prediction for a specific patient"""
    # Get patient
    patient = get_object_or_404(Patient, id=patient_id)
    
    if request.method == "POST":
        try:
            # Get doctor (current user must be a doctor)
            try:
                doctor = Doctor.objects.get(user=request.user)
            except Doctor.DoesNotExist:
                doctor = None
            
            # --- INPUT PARSING ---
            # Diabetes Inputs
            age = parse_float(request.POST.get('age'))
            bmi = parse_float(request.POST.get('bmi'))
            glucose = parse_float(request.POST.get('glucose'))
            
            bp_diabetes_raw = request.POST.get('blood_pressure', '')
            bp_systolic = None
            bp_diastolic = None
            if bp_diabetes_raw:
                try:
                    bp_parts = bp_diabetes_raw.split('/')
                    if len(bp_parts) > 1:
                        # Format is "120/80" -> Take 80 (Diastolic)
                        bp_systolic = parse_float(bp_parts[0])
                        bp_diastolic = parse_float(bp_parts[1])
                    else:
                        # Format is "80" -> Assume Diastolic provided directly
                        bp_diastolic = parse_float(bp_parts[0])
                except:
                    pass
            
            # Kidney Inputs
            creatinine = parse_float(request.POST.get('creatinine'))
            potassium = parse_float(request.POST.get('potassium'))
            hemoglobin = parse_float(request.POST.get('hemoglobin'))
            sodium = parse_float(request.POST.get('sodium'))
            urea = parse_float(request.POST.get('urea'))
            albumin_val = parse_float(request.POST.get('albumin')) 
            
            rbc_raw = request.POST.get('rbc', '') # Categorical
            rbc_val = 0.0 if rbc_raw.lower() == "abnormal" else 1.0
            
            kidney_bp_raw = request.POST.get('kidney_bp', '')
            kidney_bp = None
            if kidney_bp_raw:
                try:
                    k_bp_parts = kidney_bp_raw.split('/')
                    if len(k_bp_parts) > 1:
                        kidney_bp = parse_float(k_bp_parts[1]) # Take Diastolic
                    else:
                        kidney_bp = parse_float(k_bp_parts[0]) # Assume Diastolic
                except:
                    pass
            
            # Fallback for Kidney BP using Diabetes BP if valid
            if kidney_bp is None and bp_diastolic is not None:
                kidney_bp = bp_diastolic

            # --- MODEL EXECUTION CONTROL ---
            
            # Initialize Results
            diabetes_prob = None
            diabetes_label = None
            diabetes_risk = "Insufficient Data"
            
            kidney_prob = None
            kidney_label = None
            kidney_risk = "Insufficient Data"
            
            # Initialize Features for Saving
            # We ONLY save features that were actually provided and valid
            diabetes_features_to_save = {}
            kidney_features_to_save = {}

            # Load Models
            print("DEBUG: Loading models...")
            diabetes_model, diabetes_scaler, kidney_model, kidney_scaler = load_models()
            print("DEBUG: Models loaded.")

            # --- DIABETES PREDICTION ---
            # Check Requirements: Age, BMI, Glucose, BP_Diastolic
            if age is not None and bmi is not None and glucose is not None and bp_diastolic is not None:
                # Validation / Clamping (mg/dL units - matching training data)
                d_age = max(21, min(100, age))
                d_bmi = max(10, min(70, bmi)) # Relaxed BMI
                d_glucose = max(70, min(400, glucose)) # Glucose in mg/dL (no conversion needed)
                # BP is Diastolic now. Typical range 40-130. 
                # Training data has values like 72, 66, 64. Clip to reasonable range.
                d_bp = max(40, min(130, bp_diastolic))
                
                diabetes_input = [d_age, d_bmi, d_bp, d_glucose]
                
                # Save values for display (already in correct units)
                diabetes_features_to_save = {
                    'Age': d_age, 'BMI': d_bmi, 'BloodPressure': d_bp, 'Glucose': d_glucose
                }
                
                try:
                    diabetes_input_array = np.asarray([diabetes_input], dtype=np.float64)
                    diabetes_input_scaled = diabetes_scaler.transform(diabetes_input_array)
                    
                    diabetes_prob = float(diabetes_model.predict_proba(diabetes_input_scaled)[0][1] * 100)
                    if diabetes_prob > 95.0: diabetes_prob = 95.0
                    
                    diabetes_label = int(diabetes_model.predict(diabetes_input_scaled)[0])
                    diabetes_risk = calculate_risk_level(diabetes_prob / 100.0)
                    print(f"DEBUG: Diabetes Risk: {diabetes_risk}")
                except Exception as e:
                    print(f"ERROR: Diabetes Model Failed: {e}")
                    diabetes_risk = "Error"
            else:
                print("DEBUG: Skipping Diabetes - Missing Inputs")
                # Add partial features to save list even if skipped? 
                # User said "Only include values that are NOT None".
                if age is not None: diabetes_features_to_save['Age'] = age
                if bmi is not None: diabetes_features_to_save['BMI'] = bmi
                if glucose is not None: diabetes_features_to_save['Glucose'] = glucose
                if bp_diastolic is not None: diabetes_features_to_save['BloodPressure'] = bp_diastolic

            # --- KIDNEY PREDICTION ---
            # Requirements: Creatinine, Potassium, Hemoglobin, Sodium, BP, RBC, Urea, Albumin
            
            if (creatinine is not None and potassium is not None and hemoglobin is not None and 
                sodium is not None and kidney_bp is not None and urea is not None and albumin_val is not None):
                
                # Validation / Clamping (mg/dL units - matching training data)
                k_creatinine = max(0.4, min(15, creatinine))  # mg/dL (no conversion needed)
                k_potassium = max(2.0, min(7.0, potassium))   # mEq/L
                k_hemoglobin = max(4.0, min(20, hemoglobin))  # g/dL
                k_sodium = max(100, min(180, sodium))         # mEq/L
                k_bp = max(50, min(180, kidney_bp))           # mmHg
                k_urea = max(5, min(400, urea))               # mg/dL (no conversion needed)
                k_albumin = max(0, min(5, albumin_val))
                
                import pandas as pd
                kidney_df = pd.DataFrame({
                    'Creatinine': [k_creatinine],      # Already in mg/dL
                    'Pottasium': [k_potassium],
                    'Hemoglobin': [k_hemoglobin],
                    'Sodium': [k_sodium],
                    'Blood Pressure': [k_bp],
                    'Red Blood Cell': [rbc_val],
                    'Urea': [k_urea],                  # Already in mg/dL
                    'Albumin': [k_albumin]
                })
                
                kidney_features_to_save = {
                    'Creatinine': k_creatinine, 'Pottasium': k_potassium, 'Hemoglobin': k_hemoglobin,
                    'Sodium': k_sodium, 'Blood Pressure': k_bp, 'Red Blood Cell': rbc_val,
                    'Urea': k_urea, 'Albumin': k_albumin
                }
                
                try:
                    kidney_input_scaled = kidney_scaler.transform(kidney_df)
                    kidney_prob = float(kidney_model.predict_proba(kidney_input_scaled)[0][1] * 100)
                    if kidney_prob > 95.0: kidney_prob = 95.0
                    
                    kidney_label = int(kidney_prob >= 50.0)
                    kidney_risk = calculate_risk_level(kidney_prob / 100.0)
                    print(f"DEBUG: Kidney Risk: {kidney_risk}")
                except Exception as e:
                    print(f"ERROR: Kidney Model Failed: {e}")
                    kidney_risk = "Error"
            else:
                print("DEBUG: Skipping Kidney - Missing Inputs")
                if creatinine is not None: kidney_features_to_save['Creatinine'] = creatinine
                if potassium is not None: kidney_features_to_save['Pottasium'] = potassium
                if hemoglobin is not None: kidney_features_to_save['Hemoglobin'] = hemoglobin
                if sodium is not None: kidney_features_to_save['Sodium'] = sodium
                if kidney_bp is not None: kidney_features_to_save['Blood Pressure'] = kidney_bp
                if urea is not None: kidney_features_to_save['Urea'] = urea
                if albumin_val is not None: kidney_features_to_save['Albumin'] = albumin_val
                # RBC is always valid default

            # Create prediction object
            prediction = Prediction.objects.create(
                patient=patient,
                doctor=doctor,
                diabetes_probability=diabetes_prob,
                diabetes_label=diabetes_label,
                diabetes_risk=diabetes_risk[0:20], # Safety truncate to max_length=20
                kidney_probability=kidney_prob,
                kidney_label=kidney_label,
                kidney_risk=kidney_risk[0:20], # Safety truncate to max_length=20
                approval_status="Pending"
            )
            
            # --- Explainability & Recommendations ---
            # Only run if we have a valid risk calculated (not Insufficient Data or Error)
            
            d_explanation = ""
            k_explanation = ""
            d_shap_details = {}
            k_shap_details = {}
            
            if diabetes_risk not in ["Insufficient Data", "Error"]:
                try:
                    from .explainability import generate_patient_shap
                    import pandas as pd
                    
                    # Background data loading (abbreviated for brevity, assuming similar to before but cached/handled)
                    # For now passing None to skip expensive BG loading if not critical, or reload if needed.
                    # Re-implementing simplified BG load to prevent regression
                    try:
                        diabetes_bg = pd.read_csv('predictions/ml/diabetes.csv')
                        diabetes_bg = diabetes_bg[['Age', 'BMI', 'BloodPressure', 'Glucose']].iloc[:50]
                        diabetes_bg_scaled = diabetes_scaler.transform(diabetes_bg)
                    except:
                        diabetes_bg_scaled = None
                        
                    d_feat_names = ['Age', 'BMI', 'BloodPressure', 'Glucose']
                    
                    d_shap_path, d_explanation, d_shap_details = generate_patient_shap(
                        diabetes_model, diabetes_scaler, diabetes_input, d_feat_names, 
                        prediction.id, 'diabetes', risk_level=diabetes_risk, background_data=diabetes_bg_scaled
                    )
                    prediction.diabetes_shap_image = d_shap_path
                except Exception as e:
                    print(f"Error Diabetes Explainability: {e}")

            if kidney_risk not in ["Insufficient Data", "Error"]:
                try:
                    from .explainability import generate_patient_shap
                    import pandas as pd
                    
                    try:
                        df1 = pd.read_csv('predictions/ml/kidney.csv')
                        rename_map = {
                            'Bp': 'Blood Pressure', 'Sg': 'Specific Gravity', 'Al': 'Albumin', 'Su': 'Sugar',
                            'Rbc': 'Red Blood Cell', 'Bu': 'Urea', 'Sc': 'Creatinine', 'Sod': 'Sodium',
                            'Pot': 'Pottasium', 'Hemo': 'Hemoglobin', 'Wbcc': 'White Blood Cell Count',
                            'Rbcc': 'Red Blood Cell Count', 'Htn': 'Hypertension', 'Class': 'Predicted Class'
                        }
                        df1.rename(columns=rename_map, inplace=True)
                        required_cols = ['Creatinine', 'Pottasium', 'Hemoglobin', 'Sodium', 'Blood Pressure', 'Red Blood Cell', 'Urea', 'Albumin']
                        kidney_bg_raw = df1[required_cols].iloc[:50]
                        kidney_bg = kidney_scaler.transform(kidney_bg_raw)
                    except:
                        kidney_bg = None

                    k_feat_names = ['Creatinine', 'Pottasium', 'Hemoglobin', 'Sodium', 'Blood Pressure', 'Red Blood Cell', 'Urea', 'Albumin']
                    
                    # Reconstruct input array (all values already in correct units)
                    k_input_vals = [k_creatinine, k_potassium, k_hemoglobin, k_sodium, k_bp, rbc_val, k_urea, k_albumin]
                    
                    k_shap_path, k_explanation, k_shap_details = generate_patient_shap(
                        kidney_model, kidney_scaler, k_input_vals, k_feat_names, 
                        prediction.id, 'kidney', risk_level=kidney_risk, background_data=kidney_bg
                    )
                    prediction.kidney_shap_image = k_shap_path
                except Exception as e:
                    print(f"Error Kidney Explainability: {e}")


            # Save Explanations
            prediction.diabetes_explanation = d_explanation
            prediction.kidney_explanation = k_explanation

            # Save Features
            for name, val in diabetes_features_to_save.items():
                PredictionFeature.objects.create(
                    prediction=prediction, feature_name=f"Diabetes_{name}", feature_value=str(val), shap_value=0.0
                )
            for name, val in kidney_features_to_save.items():
                PredictionFeature.objects.create(
                    prediction=prediction, feature_name=f"Kidney_{name}", feature_value=str(val), shap_value=0.0
                )
            
            # Use Recommendations Engine
            try:
                features_dict = {}
                features_dict.update(diabetes_features_to_save)
                features_dict.update(kidney_features_to_save)
                # Map keys to match engine expectation if needed (engine uses same keys usually)
                
                # Engine fallback if Insufficient Data?
                # The engine likely expects valid inputs.
                # We should only call engine if we have minimal data.
                # Or pass what we have and let engine handle?
                # Safe approach: Only call if at least one risk is calculated.
                
                if diabetes_features_to_save or kidney_features_to_save:
                     shap_summary = {
                        'diabetes_top_features': d_shap_details.get('top_positive', [])[:3],
                        'kidney_top_features': k_shap_details.get('top_positive', [])[:3]
                    }
                     
                     # Need to normalize keys for recommendation engine?
                     # Engine uses: Age, BMI, Glucose, BP_Systolic, Creatinine...
                     # My keys: Age, BMI, Glucose, BloodPressure...
                     # Map 'BloodPressure' -> 'BP_Systolic'
                     eng_features = features_dict.copy()
                     if 'BloodPressure' in eng_features:
                         eng_features['BP_Systolic'] = eng_features.pop('BloodPressure')
                     if 'Blood Pressure' in eng_features:
                         # Kidney BP
                         if 'BP_Systolic' not in eng_features: # Use kidney BP if diabetes BP missing
                             eng_features['BP_Systolic'] = eng_features.pop('Blood Pressure')
                     
                     rec_text, d_interp, k_interp = generate_recommendation(
                        prediction, eng_features, shap_summary=shap_summary
                     )
                     prediction.recommendation_text = rec_text
                     if d_interp: prediction.diabetes_explanation = f"{d_interp} {d_explanation}"
                     if k_interp: prediction.kidney_explanation = f"{k_interp} {k_explanation}"
            
            except Exception as e:
                print(f"Error generating recommendation: {e}")

            prediction.save()
            return redirect('review_prediction', id=prediction.id)
            
        except Exception as e:
            import traceback
            import sys
            print(f"ERROR: {e}", file=sys.stderr)
            traceback.print_exc()
            return render(request, "predictions/create_prediction.html", {
                "patient": patient,
                "error": f"Error creating prediction: {str(e)}"
            })
    
    patient_name = patient.user.get_full_name() or patient.user.username
    return render(request, "predictions/create_prediction.html", {
        "patient": patient,
        "patient_name": patient_name
    })


@login_required
def review_prediction(request, id):
    """Doctor reviews and approves/rejects prediction"""
    prediction = get_object_or_404(Prediction, id=id)
    
    if request.method == "POST":
        action = request.POST.get('action')
        
        if action == 'approve':
            prediction.approval_status = "Approved"
            prediction.approved_at = timezone.now()
            prediction.reviewed_at = timezone.now()
            prediction.recommendation_text = request.POST.get('recommendation_text', prediction.recommendation_text)
            prediction.doctor_notes = request.POST.get('doctor_notes', '')
            
            try:
                prediction.doctor = Doctor.objects.get(user=request.user)
            except Doctor.DoesNotExist:
                pass
            
            prediction.save()
            return redirect('doctor_dashboard')
            
        elif action == 'reject':
            prediction.approval_status = "Rejected"
            prediction.reviewed_at = timezone.now()
            prediction.doctor_notes = request.POST.get('doctor_notes', 'Prediction rejected')
            
            try:
                prediction.doctor = Doctor.objects.get(user=request.user)
            except Doctor.DoesNotExist:
                pass
            
            prediction.save()
            return redirect('doctor_dashboard')
    
    features = PredictionFeature.objects.filter(prediction=prediction)
    
    return render(request, "predictions/review_prediction.html", {
        "prediction": prediction,
        "features": features
    })


@login_required
def prediction_detail(request, id):
    """Patient views approved prediction details"""
    prediction = get_object_or_404(Prediction, id=id)
    features = PredictionFeature.objects.filter(prediction=prediction)
    
    if hasattr(request.user, 'doctor'):
        template_name = "predictions/doctor_prediction_detail.html"
    else:
        template_name = "predictions/prediction_detail.html"
        
    return render(request, template_name, {
        "prediction": prediction,
        "features": features
    })


@login_required
def prediction_list(request):
    """List all predictions for current user"""
    if request.user.is_superuser:
        predictions = Prediction.objects.all().order_by('-created_at')
    elif hasattr(request.user, 'patient'):
        predictions = Prediction.objects.filter(patient=request.user.patient).order_by('-created_at')
    elif hasattr(request.user, 'doctor'):
        predictions = Prediction.objects.filter(doctor=request.user.doctor).order_by('-created_at')
    else:
        predictions = Prediction.objects.none()
    
    return render(request, "predictions/prediction_list.html", {
        "predictions": predictions
    })
