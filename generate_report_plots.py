
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import confusion_matrix, classification_report, roc_curve, auc, accuracy_score
from imblearn.over_sampling import SMOTE
import joblib
import os

# Set style
plt.style.use('default')  # Use default to avoid errors if seaborn styles not available
sns.set_theme(style="whitegrid")

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# If running from medpredict, paths are correct
ML_PATH = os.path.join(BASE_DIR, "predictions/ml")
DIABETES_CSV = os.path.join(ML_PATH, "diabetes.csv")
KIDNEY_CSV = os.path.join(ML_PATH, "kidney.csv")
OUTPUT_DIR = os.path.join(ML_PATH, "plots")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

print(f"Outputting plots to: {OUTPUT_DIR}")

def evaluate_diabetes():
    print("\n" + "="*50)
    print("Evaluating Diabetes Model (Replicating Training Logic)")
    print("="*50)
    
    # 1. Load Data
    df = pd.read_csv(DIABETES_CSV)
    
    # 2. Imputation (Same as train_diabetes_model.py)
    zero_impute_cols = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
    for col in zero_impute_cols:
        if col in df.columns:
            median_val = df[df[col] != 0][col].median()
            df[col] = df[col].replace(0, median_val)

    # 3. Select Features
    df = df[['Age', 'BMI', 'BloodPressure', 'Glucose', 'Outcome']]
    X = df.drop("Outcome", axis=1)
    y = df["Outcome"]

    # 4. Split (Match Training Random State)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=15)
    
    # 5. Load Model (The deployed model)
    model_path = os.path.join(ML_PATH, "diabetes_model.pkl")
    scaler_path = os.path.join(ML_PATH, "diab_scaler.pkl")
    
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    
    # 6. Predict
    X_test_scaled = scaler.transform(X_test)
    y_pred = model.predict(X_test_scaled)
    y_prob = model.predict_proba(X_test_scaled)[:, 1]
    
    # A. Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    acc = accuracy_score(y_test, y_pred)
    
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['Negative', 'Positive'],
                yticklabels=['Negative', 'Positive'])
    plt.title(f'Diabetes Model Confusion Matrix\nTest Accuracy: {acc:.2%}')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "diabetes_confusion_matrix.png"))
    plt.close()
    
    # B. ROC Curve
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    roc_auc = auc(fpr, tpr)
    
    plt.figure(figsize=(6, 5))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Diabetes Receiver Operating Characteristic (ROC)')
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "diabetes_roc_curve.png"))
    plt.close()
    
    print(f"Diabetes Test Accuracy: {acc:.4f}")
    print(classification_report(y_test, y_pred))


def evaluate_kidney():
    print("\n" + "="*50)
    print("Evaluating Kidney Model (Replicating Training Logic)")
    print("="*50)
    
    # 1. Load Data
    df = pd.read_csv(KIDNEY_CSV)
    
    # 2. Rename & Select (Same as train_kidney_model.py)
    rename_map = {
        'Bp': 'Blood Pressure', 'Sg': 'Specific Gravity', 'Al': 'Albumin', 'Su': 'Sugar',
        'Rbc': 'Red Blood Cell', 'Bu': 'Urea', 'Sc': 'Creatinine', 'Sod': 'Sodium',
        'Pot': 'Pottasium', 'Hemo': 'Hemoglobin', 'Wbcc': 'White Blood Cell Count',
        'Rbcc': 'Red Blood Cell Count', 'Htn': 'Hypertension', 'Class': 'Predicted Class'
    }
    df.rename(columns=rename_map, inplace=True)
    
    required_cols = ['Predicted Class', 'Creatinine', 'Pottasium', 'Hemoglobin', 
                     'Sodium', 'Blood Pressure', 'Red Blood Cell', 'Urea', 'Albumin']
    df = df[required_cols]
    
    # 3. Cleaning (Same outliers logic)
    df = df[df['Pottasium'] <= 7]
    df = df[df['Hemoglobin'] <= 20]
    df = df[df['Blood Pressure'] >= 50]
    
    # Winsorization (Critical to match training distribution)
    df['Creatinine'] = df['Creatinine'].clip(0, 15)
    df['Pottasium'] = df['Pottasium'].clip(2, 7)
    df['Hemoglobin'] = df['Hemoglobin'].clip(4, 20)
    df['Sodium'] = df['Sodium'].clip(100, 180)
    df['Blood Pressure'] = df['Blood Pressure'].clip(60, 180)
    
    X = df.drop("Predicted Class", axis=1)
    y = df["Predicted Class"]
    
    # 4. Split (Match Training Random State)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=15)
    
    # 5. Load Model
    model_path = os.path.join(ML_PATH, "kidney_model.pkl")
    scaler_path = os.path.join(ML_PATH, "kid_scaler.pkl")
    
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    
    # 6. Predict
    X_test_scaled = scaler.transform(X_test)
    y_pred = model.predict(X_test_scaled)
    # Check if probability available (RF usually yes)
    try:
        y_prob = model.predict_proba(X_test_scaled)[:, 1]
    except:
        y_prob = None

    # A. Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    acc = accuracy_score(y_test, y_pred)
    
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Reds',
                xticklabels=['No CKD', 'CKD'],
                yticklabels=['No CKD', 'CKD'])
    plt.title(f'Kidney Model Confusion Matrix\nTest Accuracy: {acc:.2%}')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "kidney_confusion_matrix.png"))
    plt.close()
    
    # B. ROC Curve
    if y_prob is not None:
        fpr, tpr, _ = roc_curve(y_test, y_prob)
        roc_auc = auc(fpr, tpr)
        
        plt.figure(figsize=(6, 5))
        plt.plot(fpr, tpr, color='darkred', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Kidney Receiver Operating Characteristic (ROC)')
        plt.legend(loc="lower right")
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, "kidney_roc_curve.png"))
        plt.close()
    
    print(f"Kidney Test Accuracy: {acc:.4f}")
    print(classification_report(y_test, y_pred))

if __name__ == "__main__":
    evaluate_diabetes()
    evaluate_kidney()
    print("\nProcessing Complete. Plots saved to predictions/ml/plots/")
