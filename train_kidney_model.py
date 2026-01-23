import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import joblib
import os

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ML_PATH = os.path.join(BASE_DIR, "predictions/ml")
CSV_PATH = os.path.join(ML_PATH, "kidney.csv")
MODEL_PATH = os.path.join(ML_PATH, "kidney_model.pkl")
SCALER_PATH = os.path.join(ML_PATH, "kid_scaler.pkl")

print("="*60)
print("KIDNEY MODEL TRAINING")
print("="*60)

# Load dataset
print(f"\n1. Loading dataset from: {CSV_PATH}")
df1 = pd.read_csv(CSV_PATH)
print(f"   Dataset shape: {df1.shape}")
print(f"   Columns: {df1.columns.tolist()}")

# Rename columns
print("\n2. Renaming columns...")
rename_map = {
    'Bp': 'Blood Pressure',
    'Sg': 'Specific Gravity',
    'Al': 'Albumin',
    'Su': 'Sugar',
    'Rbc': 'Red Blood Cell',
    'Bu': 'Urea',
    'Sc': 'Creatinine',
    'Sod': 'Sodium',
    'Pot': 'Pottasium',  # Keep the typo as expected by the app
    'Hemo': 'Hemoglobin',
    'Wbcc': 'White Blood Cell Count',
    'Rbcc': 'Red Blood Cell Count',
    'Htn': 'Hypertension',
    'Class': 'Predicted Class'
}

df1.rename(columns=rename_map, inplace=True)

# Selecting features needed for training
print("\n3. Selecting required features...")
required_cols = ['Predicted Class', 'Creatinine', 'Pottasium', 'Hemoglobin', 
                 'Sodium', 'Blood Pressure', 'Red Blood Cell', 'Urea', 'Albumin']
df1 = df1[required_cols]
print(f"   Selected features: {[c for c in required_cols if c != 'Predicted Class']}")

# Data cleaning
print("\n4. Cleaning data (removing outliers)...")
initial_size = len(df1)

# Remove impossible values
df1 = df1[df1['Pottasium'] <= 7]
df1 = df1[df1['Hemoglobin'] <= 20]
df1 = df1[df1['Blood Pressure'] >= 50]

# Fix sodium scale (Already correct in CSV, usually 135-145)
# df1['Sodium'] = df1['Sodium'] * 10 


# Winsorize outliers
df1['Creatinine'] = df1['Creatinine'].clip(0, 15)
df1['Pottasium'] = df1['Pottasium'].clip(2, 7)
df1['Hemoglobin'] = df1['Hemoglobin'].clip(4, 20)
df1['Sodium'] = df1['Sodium'].clip(100, 180)
df1['Blood Pressure'] = df1['Blood Pressure'].clip(60, 180)

print(f"   Removed {initial_size - len(df1)} outlier rows")
print(f"   Final dataset size: {len(df1)}")

# Prepare features and target
X = df1.drop("Predicted Class", axis=1)
y = df1["Predicted Class"]

print(f"\n5. Target distribution:\n{y.value_counts()}")

# Split data
print("\n6. Splitting data (80% train, 20% test)...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=15)
print(f"   Train size: {X_train.shape[0]}, Test size: {X_test.shape[0]}")

# Scaling
print("\n7. Scaling features with RobustScaler...")
scaler = RobustScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Model training
print("\n8. Training multiple models...")
models = {
    "Logistic Regression": LogisticRegression(random_state=42),
    "K-Nearest Neighbors": KNeighborsClassifier(n_neighbors=3),
    "Decision Tree": DecisionTreeClassifier(random_state=42),
    "Random Forest": RandomForestClassifier(random_state=42),
    "Support Vector Machine": SVC(random_state=42, probability=True),
}

results = {}
best_model_name = ""
best_accuracy = -1
best_model = None

for name, model in models.items():
    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    results[name] = accuracy
    print(f"   - {name}: {accuracy:.4f}")
    
    if accuracy > best_accuracy:
        best_accuracy = accuracy
        best_model_name = name
        best_model = model

# Save the best model
print("\n9. Saving best model...")
if best_model is not None:
    joblib.dump(best_model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    print(f"   [OK] Best Model: {best_model_name} (Accuracy: {best_accuracy:.4f})")
    print(f"   [OK] Saved: {MODEL_PATH}")
    print(f"   [OK] Saved: {SCALER_PATH}")
else:
    print("   ✗ Error: No model was trained successfully!")

print("\n" + "="*60)
print("KIDNEY MODEL TRAINING COMPLETE!")
print("="*60)
