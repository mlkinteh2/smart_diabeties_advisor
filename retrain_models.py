import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import RobustScaler
import joblib
import os
import sys

# Force AppData path
user_site = os.path.expanduser(r"~\AppData\Roaming\Python\Python312\site-packages")
if os.path.exists(user_site) and user_site not in sys.path:
    sys.path.insert(0, user_site)

# Paths
ml_dir = 'predictions/ml'

# 1. Diabetes
print(f"Training Diabetes...")
try:
    d_data = pd.read_csv(os.path.join(ml_dir, 'diabetes.csv'))
    d_features = ['Age', 'BMI', 'BloodPressure', 'Glucose']
    X_d = d_data[d_features]
    y_d = d_data['Outcome']

    d_scaler = RobustScaler()
    X_d_scaled = d_scaler.fit_transform(X_d)

    d_model = RandomForestClassifier(n_estimators=100, random_state=42)
    d_model.fit(X_d_scaled, y_d)

    joblib.dump(d_model, os.path.join(ml_dir, 'diabetes_model.pkl'))
    joblib.dump(d_scaler, os.path.join(ml_dir, 'diab_scaler.pkl'))
    print("Diabetes Saved.")
except Exception as e:
    print(f"Error Diabetes: {e}")

# 2. Kidney
print(f"Training Kidney...")
try:
    k_data = pd.read_csv(os.path.join(ml_dir, 'kidney.csv'))
    k_cols = ['Sc', 'Pot', 'Hemo', 'Sod', 'Bp', 'Rbc', 'Bu', 'Al']
    k_map = {
        'Sc': 'Creatinine', 'Pot': 'Pottasium', 'Hemo': 'Hemoglobin', 
        'Sod': 'Sodium', 'Bp': 'Blood Pressure', 'Rbc': 'Red Blood Cell', 
        'Bu': 'Urea', 'Al': 'Albumin'
    }
    X_k = k_data[k_cols].rename(columns=k_map)
    y_k = k_data['Class']

    k_scaler = RobustScaler()
    X_k_scaled = k_scaler.fit_transform(X_k)

    k_model = RandomForestClassifier(n_estimators=100, random_state=42)
    k_model.fit(X_k_scaled, y_k)

    joblib.dump(k_model, os.path.join(ml_dir, 'kidney_model.pkl'))
    joblib.dump(k_scaler, os.path.join(ml_dir, 'kid_scaler.pkl'))
    print("Kidney Saved.")

except Exception as e:
    print(f"Error Kidney: {e}")

print("Done.")
