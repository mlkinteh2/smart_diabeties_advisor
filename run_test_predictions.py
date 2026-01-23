import pandas as pd
import numpy as np
import joblib
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, accuracy_score, f1_score, classification_report

def get_clinical_diabetes_label(glucose, age):
    """
    Generate assumed ground truth based on clinical thresholds.
    Diabetes: Random Glucose > 200 mg/dL or Fasting > 126 mg/dL.
    Prediabetes: 140-199 mg/dL.
    We'll use a conservative threshold of 140 mg/dL given the context.
    """
    if pd.isna(glucose): return "Unknown"
    if glucose >= 140:
        return "Positive"
    return "Negative"

def get_clinical_kidney_label(creatinine, urea, hemoglobin):
    """
    Generate assumed ground truth based on clinical thresholds for CKD.
    Creatinine > 1.2 mg/dL (females) or 1.4 mg/dL (males) is concerning.
    Urea > 50 mg/dL is high.
    Hemoglobin < 12 g/dL (females) or < 13 g/dL (males) is anemia (common in CKD).
    """
    if pd.isna(creatinine): return "Unknown"
    
    # Simple composite rule
    risk_score = 0
    if creatinine > 1.3: risk_score += 2
    if pd.notna(urea) and urea > 45: risk_score += 1
    if pd.notna(hemoglobin) and hemoglobin < 12: risk_score += 1
    
    if risk_score >= 2:
        return "CKD"
    return "No CKD"

def run_evaluation():
    print("Loading models...")
    try:
        # Load Diabetes Models
        d_model = joblib.load('predictions/ml/diabetes_model.pkl')
        d_scaler = joblib.load('predictions/ml/diab_scaler.pkl')
        
        # Load Kidney Models
        k_model = joblib.load('predictions/ml/kidney_model.pkl')
        k_scaler = joblib.load('predictions/ml/kid_scaler.pkl')
        print("Models loaded successfully.")
    except Exception as e:
        print(f"Error loading models: {e}")
        return

    print("Loading test dataset...")
    try:
        df = pd.read_excel('predictions/ml/test_dataset.xlsx')
        print(f"Loaded {len(df)} rows.")
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return

    # Store results for metrics
    true_diabetes = []
    pred_diabetes = []
    
    true_kidney = []
    pred_kidney = []

    # --- DIABETES PREDICTION ---
    print("\n--- Running Diabetes Predictions & Ground Truth Assumption ---")
    diabetes_ml_preds = []
    diabetes_clinical_truth = []
    
    for index, row in df.iterrows():
        try:
            age = row['Age']
            bmi = row['BMI']
            glucose = row['Glucose']
            
            # Unit Conversion: Glucose
            # Model expects mg/dL (Training range ~70-200+)
            # If Glucose < 50 (e.g. 6.4), it is likely mmol/L.
            if pd.notna(glucose) and glucose < 50:
                glucose = glucose * 18.0182 # Convert mmol/L -> mg/dL
            
            # Parse Blood Pressure
            bp_raw = row['Blood Pressure']
            bp = None
            if isinstance(bp_raw, str) and '/' in bp_raw:
                try:
                    parts = bp_raw.split('/')
                    bp = float(parts[1]) if len(parts) > 1 else float(parts[0])
                except: bp = None
            elif pd.notna(bp_raw):
                bp = float(bp_raw)
            
            # 1. Generate Clinical Ground Truth (Assumed)
            clinical_label = get_clinical_diabetes_label(glucose, age)
            diabetes_clinical_truth.append(clinical_label)
            
            if pd.isna(age) or pd.isna(bmi) or pd.isna(bp) or pd.isna(glucose):
                diabetes_ml_preds.append("Missing Data")
                continue
                
            # 2. Run ML Prediction
            input_features = np.array([[age, bmi, bp, glucose]])
            input_scaled = d_scaler.transform(input_features)
            pred = int(d_model.predict(input_scaled)[0])
            ml_label = "Positive" if pred == 1 else "Negative"
            diabetes_ml_preds.append(ml_label)
            
            # Collect for metrics if valid
            if clinical_label != "Unknown":
                true_diabetes.append(clinical_label)
                pred_diabetes.append(ml_label)
            
        except Exception as e:
            print(f"Error row {index}: {e}")
            diabetes_ml_preds.append("Error")
            diabetes_clinical_truth.append("Error")
            
    df['Diabetic Prediction'] = diabetes_clinical_truth  # As requested: "put target in target column"
    df['ML Predicted Diabetes'] = diabetes_ml_preds

    # --- KIDNEY PREDICTION ---
    print("\n--- Running Kidney Predictions & Ground Truth Assumption ---")
    kidney_ml_preds = []
    kidney_clinical_truth = []
    
    for index, row in df.iterrows():
        try:
            creatinine = row.get('Creatnine') 
            potassium = row.get('Potassium')
            hemoglobin = row.get('Hemoglobin')
            sodium = row.get('Sodium')
            urea = row.get('Urea')
            albumin = row.get('Albumin')
            rbc = row.get('Red blood Cell')
            
            # Unit Conversion via Heuristics
            # Model expects mg/dL.
            
            # Creatinine: if > 20 => likely umol/L (Normal ~1.0 mg/dL, ~80-100 umol/L)
            if pd.notna(creatinine) and creatinine > 20:
                creatinine = creatinine / 88.4 # umol/L -> mg/dL
                
            # Urea: if < 50 and Creatinine was High (e.g. CKD context)? 
            # Or check absolute range. Training Urea max ~400.
            # If Urea input is ~5-10, likely mmol/L (Normal 2.5-7.1). 
            # If mg/dL, 5-10 is Low/Normal.
            # Let's assume if it's small (<40) and looks like mmol/L values (e.g. mean 7.7) -> convert
            # But wait, 40 mg/dL is also valid Urea.
            # Use stricter check: Normal BUN is 7-20 mg/dL.
            # Normal Urea (mmol/L) is 2.5-7.1.
            # 7.7 mmol/L = 7.7 * 2.8 = 21.5 mg/dL.
            # Let's apply conversion if it seems low for a CKD patient or generally < 30.
            # (Heuristic: usually BUN mg/dL rises high (50+) in CKD. If we see 7.7, it's either normal mg/dL or slightly high mmol/L.
            # Given other units are SI, assume this is too.)
            if pd.notna(urea):
                # Always convert if we converted creatinine (safe assumption of dataset consistency)
                # or just force it for this dataset since we proved Glucose/Creat are SI.
                urea = urea * 2.8 # mmol/L -> mg/dL
            
            # Parse BP
            bp_raw = row.get('Blood Pressure')
            bp = None
            if isinstance(bp_raw, str) and '/' in bp_raw:
                try:
                    parts = bp_raw.split('/')
                    bp = float(parts[1]) if len(parts) > 1 else float(parts[0])
                except: bp = None
            elif pd.notna(bp_raw):
                bp = float(bp_raw)
            
            # RBC Mapping
            rbc_val = 1.0 # Default Normal
            if isinstance(rbc, str):
                if rbc.lower().strip() in ['abnormal', '0']: rbc_val = 0.0
                else: rbc_val = 1.0
            elif pd.notna(rbc):
                rbc_val = float(rbc)
            
            # 1. Generate Clinical Ground Truth
            clinical_label = get_clinical_kidney_label(creatinine, urea, hemoglobin)
            kidney_clinical_truth.append(clinical_label)

            if (pd.isna(creatinine) or pd.isna(potassium) or pd.isna(hemoglobin) or 
                pd.isna(sodium) or pd.isna(bp) or pd.isna(urea) or pd.isna(albumin)):
                kidney_ml_preds.append("Missing Data")
                continue

            # 2. Run ML Prediction
            k_input = pd.DataFrame({
                'Creatinine': [creatinine], 'Pottasium': [potassium], 'Hemoglobin': [hemoglobin],
                'Sodium': [sodium], 'Blood Pressure': [bp], 'Red Blood Cell': [rbc_val],
                'Urea': [urea], 'Albumin': [albumin]
            })
            input_scaled = k_scaler.transform(k_input)
            prob = k_model.predict_proba(input_scaled)[0][1] * 100
            pred = int(prob >= 50.0)
            
            ml_label = "CKD" if pred == 1 else "No CKD"
            kidney_ml_preds.append(ml_label)
            
            if clinical_label != "Unknown":
                true_kidney.append(clinical_label)
                pred_kidney.append(ml_label)
            
        except Exception as e:
            print(f"Error kidney row {index}: {e}")
            kidney_ml_preds.append("Error")
            kidney_clinical_truth.append("Error")

    df['kiney prediction'] = kidney_clinical_truth # As requested
    df['ML Predicted Kidney'] = kidney_ml_preds
    
    # Save results
    output_path = 'predictions/ml/test_dataset_evaluated.xlsx'
    df.to_excel(output_path, index=False)
    print(f"\nSaved evaluated dataset to {output_path}")

    # --- METRICS & VISUALIZATION ---
    print("\n" + "="*40)
    print("EVALUATION REPORT")
    print("="*40)
    
    # Diabetes Metrics
    if true_diabetes:
        print("\n--- DIABETES MODEL PERFORMANCE ---")
        acc = accuracy_score(true_diabetes, pred_diabetes)
        f1 = f1_score(true_diabetes, pred_diabetes, pos_label="Positive", average='binary')
        print(f"Accuracy: {acc:.2%}")
        print(f"F1 Score: {f1:.4f}")
        print("\nClassification Report:")
        print(classification_report(true_diabetes, pred_diabetes))
        
        # Plot Confusion Matrix
        plt.figure(figsize=(6, 5))
        cm = confusion_matrix(true_diabetes, pred_diabetes, labels=["Negative", "Positive"])
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                    xticklabels=["Pred Neg", "Pred Pos"], 
                    yticklabels=["True Neg", "True Pos"])
        plt.title(f'Diabetes Model Evaluation\nAcc: {acc:.2f}, F1: {f1:.2f}')
        plt.tight_layout()
        plt.savefig('predictions/ml/diabetes_eval_matrix.png')
        print("Saved confusion matrix: predictions/ml/diabetes_eval_matrix.png")
        plt.close()

    # Kidney Metrics
    if true_kidney:
        print("\n--- KIDNEY MODEL PERFORMANCE ---")
        acc = accuracy_score(true_kidney, pred_kidney)
        f1 = f1_score(true_kidney, pred_kidney, pos_label="CKD", average='binary')
        print(f"Accuracy: {acc:.2%}")
        print(f"F1 Score: {f1:.4f}")
        print("\nClassification Report:")
        print(classification_report(true_kidney, pred_kidney))
        
        # Plot Confusion Matrix
        plt.figure(figsize=(6, 5))
        cm = confusion_matrix(true_kidney, pred_kidney, labels=["No CKD", "CKD"])
        sns.heatmap(cm, annot=True, fmt='d', cmap='Reds', 
                    xticklabels=["Pred No CKD", "Pred CKD"], 
                    yticklabels=["True No CKD", "True CKD"])
        plt.title(f'Kidney Model Evaluation\nAcc: {acc:.2f}, F1: {f1:.2f}')
        plt.tight_layout()
        plt.savefig('predictions/ml/kidney_eval_matrix.png')
        print("Saved confusion matrix: predictions/ml/kidney_eval_matrix.png")
        plt.close()


if __name__ == "__main__":
    run_evaluation()
