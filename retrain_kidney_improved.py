"""
Retrain Kidney Model with Improved Parameters
Goal: Reduce false positives while maintaining sensitivity
"""
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import RobustScaler
from sklearn.model_selection import cross_val_score
import joblib
import os
import sys
import numpy as np

# Force AppData path
user_site = os.path.expanduser(r"~\AppData\Roaming\Python\Python312\site-packages")
if os.path.exists(user_site) and user_site not in sys.path:
    sys.path.insert(0, user_site)

ml_dir = 'predictions/ml'

print("=" * 80)
print("RETRAINING KIDNEY DISEASE MODEL")
print("=" * 80)
print()

# Load data
k_data = pd.read_csv(os.path.join(ml_dir, 'kidney.csv'))
k_cols = ['Sc', 'Pot', 'Hemo', 'Sod', 'Bp', 'Rbc', 'Bu', 'Al']
k_map = {
    'Sc': 'Creatinine', 'Pot': 'Pottasium', 'Hemo': 'Hemoglobin', 
    'Sod': 'Sodium', 'Bp': 'Blood Pressure', 'Rbc': 'Red Blood Cell', 
    'Bu': 'Urea', 'Al': 'Albumin'
}
X_k = k_data[k_cols].rename(columns=k_map)
y_k = k_data['Class']

print(f"Dataset: {len(k_data)} samples")
print(f"  Class 0 (Healthy): {sum(y_k == 0)}")
print(f"  Class 1 (Disease): {sum(y_k == 1)}")
print()

# Scale features
k_scaler = RobustScaler()
X_k_scaled = k_scaler.fit_transform(X_k)

# Train with improved parameters
print("Training model with optimized parameters...")
print("  - Using class_weight='balanced' to handle class imbalance")
print("  - Reduced max_depth to prevent overfitting")
print("  - Increased min_samples_leaf for better generalization")
print()

k_model = RandomForestClassifier(
    n_estimators=200,           # More trees for stability
    max_depth=15,               # Limit depth to prevent overfitting
    min_samples_split=10,       # Require more samples to split
    min_samples_leaf=5,         # Require more samples in leaves
    class_weight='balanced',    # Handle class imbalance
    random_state=42,
    n_jobs=-1                   # Use all CPU cores
)

k_model.fit(X_k_scaled, y_k)

# Cross-validation
print("Performing 5-fold cross-validation...")
cv_scores = cross_val_score(k_model, X_k_scaled, y_k, cv=5, scoring='accuracy')
print(f"  CV Accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std():.3f})")
print()

# Save model
joblib.dump(k_model, os.path.join(ml_dir, 'kidney_model.pkl'))
joblib.dump(k_scaler, os.path.join(ml_dir, 'kid_scaler.pkl'))
print("✓ Model and scaler saved successfully")
print()

# Feature importance
feature_importance = pd.DataFrame({
    'feature': X_k.columns,
    'importance': k_model.feature_importances_
}).sort_values('importance', ascending=False)

print("Feature Importance:")
for idx, row in feature_importance.iterrows():
    print(f"  {row['feature']:<20s}: {row['importance']:.4f}")

print()
print("=" * 80)
print("RETRAINING COMPLETE")
print("=" * 80)
