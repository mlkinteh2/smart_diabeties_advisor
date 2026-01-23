import os
import django
import numpy as np
import pandas as pd
import shap
import joblib
import matplotlib.pyplot as plt

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medpredict.settings')
django.setup()

from predictions.utils import load_models

def debug_diabetes_full_fallback():
    print("Loading models...")
    try:
        diabetes_model, diabetes_scaler, _, _ = load_models()
        print(f"Model type: {type(diabetes_model)}")
    except Exception as e:
        print(f"Failed to load models: {e}")
        return

    # User Input Simulation
    d_input = [33, 25.0, 70, 120]
    X_raw = np.asarray([d_input], dtype=np.float64)
    X_scaled = diabetes_scaler.transform(X_raw)
    
    col_names = ['Age', 'BMI', 'BloodPressure', 'Glucose']
    
    print(f"Scaled Input: {X_scaled}")
    
    explainer = None
    shap_values = None
    
    # 1. Try Tree
    try:
        print("Attempting TreeExplainer...")
        explainer = shap.TreeExplainer(diabetes_model)
        shap_values = explainer.shap_values(X_scaled)
        print("TreeExplainer Success!")
    except Exception as e:
        print(f"TreeExplainer Failed: {e}")
        
    # 2. Try Linear
    if shap_values is None:
        try:
            print("Attempting LinearExplainer...")
            explainer = shap.LinearExplainer(diabetes_model, X_scaled)
            shap_values = explainer.shap_values(X_scaled)
            print("LinearExplainer Success!")
        except Exception as e:
            print(f"LinearExplainer Failed: {e}")

    # 3. Try Kernel
    if shap_values is None:
        try:
            print("Attempting KernelExplainer...")
            background = np.zeros_like(X_scaled)
            explainer = shap.KernelExplainer(diabetes_model.predict, background)
            shap_values = explainer.shap_values(X_scaled)
            print("KernelExplainer Success!")
        except Exception as e:
            print(f"KernelExplainer Failed: {e}")
            
    if shap_values is not None:
        print(f"\nSHAP Result Type: {type(shap_values)}")
        if isinstance(shap_values, list):
            print(f"Is List. Length: {len(shap_values)}")
            print(f"Item 0 shape: {shap_values[0].shape}")
            if len(shap_values) > 1:
                print(f"Item 1 shape: {shap_values[1].shape}")
        elif isinstance(shap_values, np.ndarray):
            print(f"Is Array. Shape: {shap_values.shape}")
            print(f"Values: {shap_values}")
    else:
        print("ALL Explainers Failed.")

if __name__ == "__main__":
    debug_diabetes_full_fallback()
