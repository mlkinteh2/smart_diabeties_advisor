import os
import django
import sys
import pandas as pd
import numpy as np
import shap
import matplotlib
import matplotlib.pyplot as plt
import joblib

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medpredict.settings')
django.setup()

from predictions.utils import load_models
from predictions.explainability import generate_patient_shap, generate_global_feature_importance

def debug_kidney_pipeline():
    print("DEBUG: Starting Kidney Pipeline Check")
    
    # 1. Load Data
    try:
        csv_path = 'predictions/ml/kidney.csv'
        print(f"DEBUG: Reading {csv_path}")
        df = pd.read_csv(csv_path)
        print(f"DEBUG: Data shape: {df.shape}")
        print(f"DEBUG: Columns: {df.columns.tolist()}")
        print(f"DEBUG: First 5 rows:\n{df.head()}")
    except Exception as e:
        print(f"ERROR: Failed to read kidney.csv: {e}")
        return

    # 2. Load Models
    try:
        print("DEBUG: Loading models...")
        diabetes_model, diabetes_scaler, kidney_model, kidney_scaler = load_models()
        print(f"DEBUG: Kidney model type: {type(kidney_model)}")
        print(f"DEBUG: Kidney scaler type: {type(kidney_scaler)}")
        
        if kidney_model is None:
            print("ERROR: Kidney model is None! Retraining might be needed.")
            return
            
    except Exception as e:
        print(f"ERROR: Failed to load models: {e}")
        return

    # 3. Simulate Prediction
    # Use mean values from dataset as a test case
    rename_map = {
        'Bp': 'Blood Pressure', 'Sg': 'Specific Gravity', 'Al': 'Albumin', 'Su': 'Sugar',
        'Rbc': 'Red Blood Cell', 'Bu': 'Urea', 'Sc': 'Creatinine', 'Sod': 'Sodium',
        'Pot': 'Pottasium', 'Hemo': 'Hemoglobin', 'Wbcc': 'White Blood Cell Count',
        'Rbcc': 'Red Blood Cell Count', 'Htn': 'Hypertension', 'Class': 'Predicted Class'
    }
    df_renamed = df.rename(columns=rename_map)
    required_cols = ['Creatinine', 'Pottasium', 'Hemoglobin', 'Sodium', 'Blood Pressure', 'Red Blood Cell', 'Urea', 'Albumin']
    
    # Create a dummy input (just use the first row of clean data)
    try:
        input_data = df_renamed[required_cols].iloc[0].to_dict()
        # Apply the transformation done in views.py
        # input_data['Sodium'] = input_data['Sodium'] * 10 # REMOVED FIX
        print(f"DEBUG: Test Input Data: {input_data}")
        
        kidney_df = pd.DataFrame([input_data])
        
        # Scale
        print("DEBUG: Scaling input...")
        kidney_input_scaled = kidney_scaler.transform(kidney_df)
        print(f"DEBUG: Scaled Input: {kidney_input_scaled}")
        
        # Predict
        print("DEBUG: Predicting...")
        probs = kidney_model.predict_proba(kidney_input_scaled)
        print(f"DEBUG: Probabilities: {probs}")
        
        prediction = kidney_model.predict(kidney_input_scaled)
        print(f"DEBUG: Prediction: {prediction}")
        
    except Exception as e:
        print(f"ERROR: Prediction Failed: {e}")
        import traceback
        traceback.print_exc()

    # 4. Simulate SHAP
    print("\nDEBUG: Testing SHAP Generation...")
    try:
        # Features 
        k_feat_names = required_cols
        
        # Background data
        kidney_bg_raw = df_renamed[required_cols].iloc[:50]
        # kidney_bg_raw['Sodium'] = kidney_bg_raw['Sodium'] * 10 # Same transform - REMOVED
        
        if kidney_scaler:
            kidney_bg = kidney_scaler.transform(kidney_bg_raw)
        else:
            kidney_bg = None
            
        print(f"DEBUG: Background data shape: {kidney_bg.shape}")
        
        # Call generate_patient_shap
        # We need a dummy prediction ID
        dummy_id = 9999
        
        k_input_raw = kidney_df.iloc[0].values
        
        print("DEBUG: calling generate_patient_shap...")
        path, explanation, details = generate_patient_shap(
            kidney_model, 
            kidney_scaler, 
            k_input_raw, 
            k_feat_names, 
            dummy_id, 
            'kidney',
            risk_level='High',
            background_data=kidney_bg
        )
        
        print(f"DEBUG: SHAP Result Path: {path}")
        print(f"DEBUG: SHAP Explanation: {explanation}")
        
        if path is None:
             print("ERROR: SHAP generation returned None.")
        
    except Exception as e:
        print(f"ERROR: SHAP Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_kidney_pipeline()
