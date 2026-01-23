"""
Retrain Kidney Model using Logistic Regression
Goal: Better generalization and fewer false positives
"""
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import RobustScaler
from sklearn.model_selection import cross_val_score
import joblib
import os
import sys

# Force AppData path
user_site = os.path.expanduser(r"~\AppData\Roaming\Python\Python312\site-packages")
if os.path.exists(user_site) and user_site not in sys.path:
    sys.path.insert(0, user_site)

ml_dir = 'predictions/ml'

print("=" * 80)
print("RETRAINING KIDNEY MODEL WITH LOGISTIC REGRESSION")
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

# Scale features (important for Logistic Regression)
k_scaler = RobustScaler()
X_k_scaled = k_scaler.fit_transform(X_k)

# Train Logistic Regression
print("Training Logistic Regression model...")
print("  - Using class_weight='balanced'")
print("  - C=0.1 for regularization (prevents overfitting)")
print("  - max_iter=1000 for convergence")
print()

k_model = LogisticRegression(
    C=0.1,                      # Strong regularization
    class_weight='balanced',    # Handle class imbalance
    max_iter=1000,
    random_state=42,
    solver='lbfgs'
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

# Feature coefficients
feature_coef = pd.DataFrame({
    'feature': X_k.columns,
    'coefficient': k_model.coef_[0]
}).sort_values('coefficient', key=abs, ascending=False)

print("Feature Coefficients (sorted by absolute value):")
for idx, row in feature_coef.iterrows():
    direction = "↑ Disease" if row['coefficient'] > 0 else "↓ Disease"
    print(f"  {row['feature']:<20s}: {row['coefficient']:>8.4f}  {direction}")

print()
print("=" * 80)
print("RETRAINING COMPLETE")
print("=" * 80)
