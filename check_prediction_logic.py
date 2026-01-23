import os
import sys
import django
import numpy as np

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "medpredict.settings")
django.setup()

from predictions.utils import load_models, calculate_risk_level

def test_pipeline():
    print("--- Testing ML Pipeline ---")
    try:
        print("1. Loading models...")
        diabetes_model, diabetes_scaler, kidney_model, kidney_scaler = load_models()
        print("   SUCCESS: Models loaded.")
    except Exception as e:
        print(f"   FAIL: Model loading failed: {e}")
        return

    # Diabetes Test
    print("\n2. Testing Diabetes Prediction...")
    try:
        # Inputs: Age, BMI, BP, Glucose
        # Using dummy values: Age=50, BMI=28, BP=130, Glucose=100
        d_input = [50.0, 28.0, 130.0, 100.0]
        d_input_array = np.asarray([d_input], dtype=np.float64)
        
        print(f"   Input: {d_input}")
        d_scaled = diabetes_scaler.transform(d_input_array)
        d_prob = diabetes_model.predict_proba(d_scaled)[0][1] * 100
        d_risk = calculate_risk_level(d_prob / 100.0)
        print(f"   SUCCESS: Diabetes Risk: {d_risk} ({d_prob:.2f}%)")
    except Exception as e:
        print(f"   FAIL: Diabetes prediction failed: {e}")
        import traceback
        traceback.print_exc()

    # Kidney Test
    print("\n3. Testing Kidney Prediction...")
    try:
        import pandas as pd
        # Inputs matched to views.py logic
        k_data = {
            'Creatinine': [1.0],
            'Pottasium': [4.0],
            'Hemoglobin': [14.0],
            'Sodium': [140.0],
            'Blood Pressure': [80.0],
            'Red Blood Cell': [1.0], # Normal
            'Urea': [30.0],
            'Albumin': [0.0]
        }
        k_df = pd.DataFrame(k_data)
        print(f"   Input: {k_df.to_dict(orient='records')[0]}")
        
        k_scaled = kidney_scaler.transform(k_df)
        k_prob = kidney_model.predict_proba(k_scaled)[0][1] * 100
        k_risk = calculate_risk_level(k_prob / 100.0)
        print(f"   SUCCESS: Kidney Risk: {k_risk} ({k_prob:.2f}%)")
    except Exception as e:
        print(f"   FAIL: Kidney prediction failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pipeline()
