import pandas as pd
import numpy as np
import joblib
import os
import sys

# Force AppData path
user_site = os.path.expanduser(r"~\AppData\Roaming\Python\Python312\site-packages")
if os.path.exists(user_site) and user_site not in sys.path:
    sys.path.insert(0, user_site)

ml_dir = 'predictions/ml'

# Load the kidney model and scaler
k_model = joblib.load(os.path.join(ml_dir, 'kidney_model.pkl'))
k_scaler = joblib.load(os.path.join(ml_dir, 'kid_scaler.pkl'))

print("=== Testing Kidney Model ===\n")

# Test Case 1: Healthy patient (from row 252 of CSV - first healthy patient)
print("Test 1: Healthy Patient (from CSV row 252)")
print("Values: Bp=80, Sc=1.0, Bu=10, Sod=135, Pot=5.0, Hemo=15.0, Rbc=1.0, Al=0")
print("Expected: Low Risk (Class=0)\n")

healthy_df = pd.DataFrame({
    'Creatinine': [1.0],
    'Pottasium': [5.0],
    'Hemoglobin': [15.0],
    'Sodium': [135.0],
    'Blood Pressure': [80.0],
    'Red Blood Cell': [1.0],
    'Urea': [10.0],
    'Albumin': [0.0]
})

healthy_scaled = k_scaler.transform(healthy_df)
healthy_prob = k_model.predict_proba(healthy_scaled)[0][1] * 100
print(f"Predicted Probability: {healthy_prob:.1f}%")
print(f"Risk Level: {'Low' if healthy_prob < 30 else 'Medium' if healthy_prob < 70 else 'High'}\n")

# Test Case 2: Diseased patient (from row 2 of CSV)
print("Test 2: Diseased Patient (from CSV row 2)")
print("Values: Bp=80, Sc=1.2, Bu=36, Sod=137.53, Pot=4.63, Hemo=15.4, Rbc=1.0, Al=1.0")
print("Expected: High Risk (Class=1)\n")

diseased_df = pd.DataFrame({
    'Creatinine': [1.2],
    'Pottasium': [4.63],
    'Hemoglobin': [15.4],
    'Sodium': [137.53],
    'Blood Pressure': [80.0],
    'Red Blood Cell': [1.0],
    'Urea': [36.0],
    'Albumin': [1.0]
})

diseased_scaled = k_scaler.transform(diseased_df)
diseased_prob = k_model.predict_proba(diseased_scaled)[0][1] * 100
print(f"Predicted Probability: {diseased_prob:.1f}%")
print(f"Risk Level: {'Low' if diseased_prob < 30 else 'Medium' if diseased_prob < 70 else 'High'}\n")

# Test Case 3: Check feature names expected by scaler
print("Test 3: Feature Names Check")
print(f"Scaler expects features in this order:")
if hasattr(k_scaler, 'feature_names_in_'):
    print(k_scaler.feature_names_in_)
else:
    print("Feature names not stored in scaler")
