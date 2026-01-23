
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report
from imblearn.over_sampling import SMOTE
import joblib
import os

# Set style
plt.style.use('default')
sns.set_theme(style="whitegrid")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ML_PATH = os.path.join(BASE_DIR, "predictions/ml")
DIABETES_CSV = os.path.join(ML_PATH, "diabetes.csv")
OUTPUT_DIR = os.path.join(ML_PATH, "plots")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def compare_features():
    print("="*60)
    print("DIABETES MODEL COMPARISON: ALL vs SELECTED FEATURES")
    print("="*60)
    
    # 1. Load Data
    df = pd.read_csv(DIABETES_CSV)
    
    # 2. Imputation (Common)
    zero_impute_cols = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
    for col in zero_impute_cols:
        if col in df.columns:
            median_val = df[df[col] != 0][col].median()
            df[col] = df[col].replace(0, median_val)
            
    # --- SCENARIO A: ALL FEATURES (Must Retrain) ---
    print("\n[SCENARIO A] Training with ALL features...")
    X_all = df.drop("Outcome", axis=1)
    y_all = df["Outcome"]
    
    # Split
    X_train_a, X_test_a, y_train_a, y_test_a = train_test_split(X_all, y_all, test_size=0.2, random_state=15)
    
    # SMOTE
    sm = SMOTE(random_state=42)
    X_train_res_a, y_train_res_a = sm.fit_resample(X_train_a, y_train_a)
    
    # Scale
    scaler_a = RobustScaler()
    X_train_scaled_a = scaler_a.fit_transform(X_train_res_a)
    X_test_scaled_a = scaler_a.transform(X_test_a)
    
    # Train
    model_a = RandomForestClassifier(random_state=42)
    model_a.fit(X_train_scaled_a, y_train_res_a)
    
    # Predict
    y_pred_a = model_a.predict(X_test_scaled_a)
    acc_a = accuracy_score(y_test_a, y_pred_a)
    print(f"Accuracy (All Features): {acc_a:.2%}")
    
    
    # --- SCENARIO B: SELECTED FEATURES (Use SAVED Model) ---
    print("\n[SCENARIO B] Using DEPLOYED Model (Consolidated Consistency)...")
    selected_cols = ['Age', 'BMI', 'BloodPressure', 'Glucose']
    
    X_sel = df[selected_cols]
    y_sel = df["Outcome"]
    
    # Split (Same seed as training script)
    X_train_b, X_test_b, y_train_b, y_test_b = train_test_split(X_sel, y_sel, test_size=0.2, random_state=15)
    
    # Load SAVED Model and Scaler
    model_path = os.path.join(ML_PATH, "diabetes_model.pkl")
    scaler_path = os.path.join(ML_PATH, "diab_scaler.pkl")
    
    # Only try to load if exists, else fallback to retraining (safety)
    if os.path.exists(model_path) and os.path.exists(scaler_path):
        print(f"Loading model from {model_path}")
        model_b = joblib.load(model_path)
        scaler_b = joblib.load(scaler_path)
        
        # Predict using Loaded Scaler
        X_test_scaled_b = scaler_b.transform(X_test_b)
        y_pred_b = model_b.predict(X_test_scaled_b)
    else:
        print("WARNING: Saved model not found, retraining...")
        # Fallback (Should not happen in your case)
        sm = SMOTE(random_state=42)
        X_train_res_b, y_train_res_b = sm.fit_resample(X_train_b, y_train_b)
        scaler_b = RobustScaler()
        X_train_scaled_b = scaler_b.fit_transform(X_train_res_b)
        model_b = RandomForestClassifier(random_state=42)
        model_b.fit(X_train_scaled_b, y_train_res_b)
        X_test_scaled_b = scaler_b.transform(X_test_b)
        y_pred_b = model_b.predict(X_test_scaled_b)

    acc_b = accuracy_score(y_test_b, y_pred_b)
    print(f"Accuracy (Deployed Model): {acc_b:.2%}")

    # --- PLOTTING ---
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Plot A
    cm_a = confusion_matrix(y_test_a, y_pred_a)
    sns.heatmap(cm_a, annot=True, fmt='d', cmap='Greens', ax=axes[0],
                xticklabels=['Neg', 'Pos'], yticklabels=['Neg', 'Pos'])
    axes[0].set_title(f'Scenario A: ALL Features\nAccuracy: {acc_a:.2%}')
    axes[0].set_xlabel('Predicted')
    axes[0].set_ylabel('True')
    
    # Plot B
    cm_b = confusion_matrix(y_test_b, y_pred_b)
    sns.heatmap(cm_b, annot=True, fmt='d', cmap='Blues', ax=axes[1],
                xticklabels=['Neg', 'Pos'], yticklabels=['Neg', 'Pos'])
    axes[1].set_title(f'Scenario B: SELECTED Features (Deployed)\nAccuracy: {acc_b:.2%}')
    axes[1].set_xlabel('Predicted')
    axes[1].set_ylabel('True')
    
    plt.tight_layout()
    plot_path = os.path.join(OUTPUT_DIR, "diabetes_feature_comparison.png")
    plt.savefig(plot_path)
    plt.close()
    
    print(f"\nComparison plot saved to: {plot_path}")

if __name__ == "__main__":
    compare_features()
