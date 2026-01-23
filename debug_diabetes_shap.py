import os
import django
import numpy as np
import pandas as pd
import shap
import joblib

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medpredict.settings')
django.setup()

from predictions.utils import load_models
from django.conf import settings

def debug_diabetes():
    print("Loading models...")
    try:
        diabetes_model, diabetes_scaler, _, _ = load_models()
        print(f"Model type: {type(diabetes_model)}")
    except Exception as e:
        print(f"Failed to load models: {e}")
        return

    # User Input Simulation (Standard values)
    # Age=33, BMI=25, BP=70, Glucose=120
    d_feat_names = ['Age', 'BMI', 'BloodPressure', 'Glucose']
    d_input = [33, 25.0, 70, 120]
    
    # Scale
    X_raw = np.asarray([d_input], dtype=np.float64)
    X_scaled = diabetes_scaler.transform(X_raw)
    
    print(f"\nScanning Input: {d_input}")
    print(f"Scaled Input: {X_scaled}")
    
    # Generate SHAP
    print("\nRunning TreeExplainer...")
    try:
        explainer = shap.TreeExplainer(diabetes_model)
        shap_values = explainer.shap_values(X_scaled)
        
        print("\n--- SHAP OUTPUT ANALYSIS ---")
        print(f"Type: {type(shap_values)}")
        
        if isinstance(shap_values, list):
            print(f"Is List. Length: {len(shap_values)}")
            for i, item in enumerate(shap_values):
                print(f"  Item {i} type: {type(item)}, shape: {item.shape}")
                print(f"  Item {i} sample values: {item[0]}")
                
            vals = shap_values[1][0] # Assuming Class 1
            print(f"\nExtracting List Index 1 (Positive Class): {vals}")
            
        elif isinstance(shap_values, np.ndarray):
            print(f"Is Array. Shape: {shap_values.shape}")
            if shap_values.ndim == 3:
                 print(f"  3D Array detected.")
                 vals = shap_values[0, :, 1]
                 print(f"  Extracted [0, :, 1]: {vals}")
            elif shap_values.ndim == 2:
                 print(f"  2D Array detected.")
                 vals = shap_values[0]
                 print(f"  Extracted [0]: {vals}")
        
    except Exception as e:
        print(f"SHAP Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_diabetes()
