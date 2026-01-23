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
from imblearn.over_sampling import SMOTE
import joblib
import os

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ML_PATH = os.path.join(BASE_DIR, "predictions/ml")
CSV_PATH = os.path.join(ML_PATH, "diabetes.csv")
MODEL_PATH = os.path.join(ML_PATH, "diabetes_model.pkl")
SCALER_PATH = os.path.join(ML_PATH, "diab_scaler.pkl")

print("="*60)
print("DIABETES MODEL TRAINING")
print("="*60)

# Load dataset
print(f"\n1. Loading dataset from: {CSV_PATH}")
df = pd.read_csv(CSV_PATH)
print(f"   Dataset shape: {df.shape}")
print(f"   Columns: {df.columns.tolist()}")

# Data Cleaning: Handling Invalid Zero Values (Imputation)
print("\n2. Handling invalid zero values...")
zero_impute_cols = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']

for col in zero_impute_cols:
    if col in df.columns:
        median_val = df[df[col] != 0][col].median()
        df[col] = df[col].replace(0, median_val)
        print(f"   - Imputed {col} zeros with median: {median_val:.2f}")

# Selecting features present in system (Age, BMI, BloodPressure, Glucose)
print("\n3. Selecting required features: Age, BMI, BloodPressure, Glucose")
df = df[['Age', 'BMI', 'BloodPressure', 'Glucose', 'Outcome']]
X = df.drop("Outcome", axis=1)
y = df["Outcome"]

print(f"   Features shape: {X.shape}")
print(f"   Target distribution:\n{y.value_counts()}")

# Split data
print("\n4. Splitting data (80% train, 20% test)...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=15)
print(f"   Train size: {X_train.shape[0]}, Test size: {X_test.shape[0]}")

# SMOTE balancing
print("\n5. Applying SMOTE for class balancing...")
sm = SMOTE(random_state=42)
X_train, y_train = sm.fit_resample(X_train, y_train)
print(f"   After SMOTE:\n{y_train.value_counts()}")

# Scaling
print("\n6. Scaling features with RobustScaler...")
scaler = RobustScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Model training
print("\n7. Training multiple models...")
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
print("\n8. Saving best model...")
if best_model is not None:
    joblib.dump(best_model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    print(f"   [OK] Best Model: {best_model_name} (Accuracy: {best_accuracy:.4f})")
    print(f"   [OK] Saved: {MODEL_PATH}")
    print(f"   [OK] Saved: {SCALER_PATH}")
else:
    print("   ✗ Error: No model was trained successfully!")

print("\n" + "="*60)
print("DIABETES MODEL TRAINING COMPLETE!")
print("="*60)
