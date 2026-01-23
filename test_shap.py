import os
import sys
import numpy as np
import joblib
import pandas as pd

# Force AppData path
user_site = os.path.expanduser(r"~\AppData\Roaming\Python\Python312\site-packages")
if os.path.exists(user_site) and user_site not in sys.path:
    sys.path.insert(0, user_site)

# Setup Django settings for standalone use (needed for settings.MEDIA_ROOT)
import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        MEDIA_ROOT=os.path.abspath("media"),
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
            'accounts',
            'predictions'
        ],
        DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}}
    )
    django.setup()

# Import after setup
try:
    from predictions.explainability import generate_patient_shap
    from predictions.utils import load_models
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

def test_shap():
    print("Loading models...")
    d_model, d_scaler, k_model, k_scaler = load_models()
    print("Models loaded.")

    # Test Diabetes SHAP
    print("\n--- Testing Diabetes SHAP ---")
    d_features = ['Age', 'BMI', 'BloodPressure', 'Glucose']
    # Dummy input: 50, 30, 120, 150
    d_input = [50, 30, 120, 150]
    
    try:
        path, text, details = generate_patient_shap(
            d_model, d_scaler, d_input, d_features, 
            999, 'diabetes_debug', risk_level="High"
        )
        print(f"Path: {path}")
        print(f"Text: {text}")
        if path:
            print("Diabetes SHAP Success")
        else:
            print("Diabetes SHAP Failed (Path is None)")
    except Exception as e:
        print(f"Diabetes SHAP Exception: {e}")
        import traceback
        traceback.print_exc()

    # Test Kidney SHAP
    print("\n--- Testing Kidney SHAP ---")
    k_features = ['Creatinine', 'Pottasium', 'Hemoglobin', 'Sodium', 'Blood Pressure', 'Red Blood Cell', 'Urea', 'Albumin']
    # Dummy input
    k_input = [1.2, 4.5, 14.0, 140, 120, 1.0, 40, 0]
    
    try:
        path, text, details = generate_patient_shap(
            k_model, k_scaler, k_input, k_features, 
            999, 'kidney_debug', risk_level="Low"
        )
        print(f"Path: {path}")
        print(f"Text: {text}")
        if path:
            print("Kidney SHAP Success")
        else:
            print("Kidney SHAP Failed (Path is None)")
    except Exception as e:
        print(f"Kidney SHAP Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_shap()
