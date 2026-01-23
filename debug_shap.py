import os
import sys
import django
import numpy as np
import pandas as pd
from pathlib import Path

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medpredict.settings')
django.setup()

from predictions.utils import load_models
from predictions.explainability import generate_global_feature_importance, generate_patient_shap
from django.conf import settings

def test_explainability_refactor():
    print("Loading models...")
    try:
        diabetes_model, diabetes_scaler, kidney_model, kidney_scaler = load_models()
        print("Models loaded successfully.")
    except Exception as e:
        print(f"Failed to load models: {e}")
        return

    # Diabetes Features (Matches train_diabetes_model.py)
    d_feat_names = ['Age', 'BMI', 'BloodPressure', 'Glucose']
    d_input = [33, 25.0, 70, 120] # Aligned order
    
    # Kidney Features (Matches train_kidney_model.py)
    # Note 'Pottasium' typo is carried over from training script
    k_feat_names = ['Creatinine', 'Pottasium', 'Hemoglobin', 'Sodium', 'Blood Pressure', 'Red Blood Cell', 'Urea', 'Albumin']
    import pandas as pd
    k_input = pd.DataFrame([np.zeros(len(k_feat_names))], columns=k_feat_names)

    # Load background data for Global FI test
    try:
        if os.path.exists('predictions/ml/diabetes.csv'):
            diabetes_bg = pd.read_csv('predictions/ml/diabetes.csv')
            diabetes_bg = diabetes_bg[['Age', 'BMI', 'BloodPressure', 'Glucose']].iloc[:50] # Match features
            diabetes_bg_scaled = diabetes_scaler.transform(diabetes_bg)
        else:
            diabetes_bg_scaled = None
            
        if os.path.exists('predictions/ml/kidney.csv'):
            # Load and rename match training script logic
            df1 = pd.read_csv('predictions/ml/kidney.csv')
            rename_map = {
                'Bp': 'Blood Pressure', 'Sg': 'Specific Gravity', 'Al': 'Albumin', 'Su': 'Sugar',
                'Rbc': 'Red Blood Cell', 'Bu': 'Urea', 'Sc': 'Creatinine', 'Sod': 'Sodium',
                'Pot': 'Pottasium', 'Hemo': 'Hemoglobin', 'Wbcc': 'White Blood Cell Count',
                'Rbcc': 'Red Blood Cell Count', 'Htn': 'Hypertension', 'Class': 'Predicted Class'
            }
            df1.rename(columns=rename_map, inplace=True)
            required_cols = ['Creatinine', 'Pottasium', 'Hemoglobin', 'Sodium', 'Blood Pressure', 'Red Blood Cell', 'Urea', 'Albumin']
            
            # Data cleaning (minimal version for backend loading)
            df1['Sodium'] = df1['Sodium'] * 10
            
            kidney_bg_raw = df1[required_cols].iloc[:50]
            kidney_bg = kidney_scaler.transform(kidney_bg_raw) 
        else:
            kidney_bg = None
    except Exception as e:
        print(f"Failed to load background data for debug: {e}")
        import traceback
        traceback.print_exc()
        diabetes_bg_scaled = None
        kidney_bg = None
    except Exception as e:
        print(f"Failed to load background data for debug: {e}")
        diabetes_bg_scaled = None
        kidney_bg = None

    print("\n--- Testing Global Feature Importance ---")
    # Diabetes Global FI
    d_fi = generate_global_feature_importance(diabetes_model, d_feat_names, 'diabetes', background_data=diabetes_bg_scaled)
    print(f"Diabetes Global FI: {d_fi}")
    
    # Kidney Global FI (Now supported via SHAP)
    k_fi = generate_global_feature_importance(kidney_model, k_feat_names, 'kidney', background_data=kidney_bg)
    print(f"Kidney Global FI: {k_fi}")
    
    print("\n--- Testing Patient SHAP ---")
    print("Generating Diabetes SHAP...")
    d_shap, d_expl = generate_patient_shap(diabetes_model, diabetes_scaler, d_input, d_feat_names, 999, 'diabetes')
    print(f"Diabetes SHAP Path: {d_shap}")
    print(f"Diabetes Explanation: {d_expl}")
    
    print("Generating Kidney SHAP...")
    # Use raw input for patient shap as expected by updated signature
    k_input_raw = k_input.iloc[0].values
    k_shap, k_expl = generate_patient_shap(kidney_model, kidney_scaler, k_input_raw, k_feat_names, 999, 'kidney')
    print(f"Kidney SHAP Path: {k_shap}")
    print(f"Kidney Explanation: {k_expl}")

    # Check File Existence
    if d_shap:
        p = Path(settings.MEDIA_ROOT) / d_shap
        print(f"Diabetes SHAP File exists? {p.exists()} at {p}")
    
    if k_shap:
        p = Path(settings.MEDIA_ROOT) / k_shap
        print(f"Kidney SHAP File exists? {p.exists()} at {p}")
    
    if k_fi:
        p = Path(settings.MEDIA_ROOT) / k_fi
        print(f"Kidney Global FI File exists? {p.exists()} at {p}")

if __name__ == "__main__":
    test_explainability_refactor()
