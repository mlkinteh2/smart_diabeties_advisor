
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.preprocessing import RobustScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import make_scorer, accuracy_score
import os

# Set style
plt.style.use('default')
sns.set_theme(style="whitegrid")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ML_PATH = os.path.join(BASE_DIR, "predictions/ml")
KIDNEY_CSV = os.path.join(ML_PATH, "kidney.csv")
OUTPUT_DIR = os.path.join(ML_PATH, "plots")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def check_kidney_overfitting():
    print("="*60)
    print("INVESTIGATING KIDNEY MODEL OVERFITTING")
    print("="*60)
    
    # 1. Load Data
    df = pd.read_csv(KIDNEY_CSV)
    print(f"Loaded Dataset: {df.shape}")
    
    # 2. Rename & Select (Match Training)
    rename_map = {
        'Bp': 'Blood Pressure', 'Sg': 'Specific Gravity', 'Al': 'Albumin', 'Su': 'Sugar',
        'Rbc': 'Red Blood Cell', 'Bu': 'Urea', 'Sc': 'Creatinine', 'Sod': 'Sodium',
        'Pot': 'Pottasium', 'Hemo': 'Hemoglobin', 'Wbcc': 'White Blood Cell Count',
        'Rbcc': 'Red Blood Cell Count', 'Htn': 'Hypertension', 'Class': 'Predicted Class'
    }
    df.rename(columns=rename_map, inplace=True)
    
    # Check 1: Data Leakage via Correlation
    print("\n[CHECK 1] Feature Correlations with Target...")
    # Map class to int temporarily
    df['Target'] = df['Predicted Class']
    
    # Compute correlation
    numeric_df = df.select_dtypes(include=[np.number])
    corr_matrix = numeric_df.corr()
    target_corr = corr_matrix['Target'].sort_values(ascending=False)
    
    print("Correlations with Target ('Target'):")
    print(target_corr)
    
    if target_corr.iloc[1] > 0.95 or target_corr.iloc[-1] < -0.95:
        print("WARNING: Extremely high correlation detected! Possible proxy variable found.")
    else:
        print("Correlations look plausible (strong predictors expected, but no 1.0 proxies).")

    # 3. Apply Training Preprocessing (Winsorization)
    required_cols = ['Predicted Class', 'Creatinine', 'Pottasium', 'Hemoglobin', 
                     'Sodium', 'Blood Pressure', 'Red Blood Cell', 'Urea', 'Albumin']
    df = df[required_cols]

    # Outlier Removal (Training Logic)
    df = df[df['Pottasium'] <= 7]
    df = df[df['Hemoglobin'] <= 20]
    df = df[df['Blood Pressure'] >= 50]
    
    # Winsorization
    df['Creatinine'] = df['Creatinine'].clip(0, 15)
    df['Pottasium'] = df['Pottasium'].clip(2, 7)
    df['Hemoglobin'] = df['Hemoglobin'].clip(4, 20)
    df['Sodium'] = df['Sodium'].clip(100, 180)
    df['Blood Pressure'] = df['Blood Pressure'].clip(60, 180)
    
    X = df.drop("Predicted Class", axis=1)
    y = df["Predicted Class"]
    
    # 4. Cross Validation (5-Fold)
    print("\n[CHECK 2] 5-Fold Cross Validation...")
    # Use Pipeline equivalent logic
    scaler = RobustScaler()
    X_scaled = scaler.fit_transform(X)
    
    model = RandomForestClassifier(random_state=42)
    
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_val_score(model, X_scaled, y, cv=cv, scoring='accuracy')
    
    print(f"CV Scores: {scores}")
    print(f"Mean CV Accuracy: {scores.mean():.4f} (+/- {scores.std() * 2:.4f})")
    
    if scores.mean() > 0.99:
        print("Result: Model allows perfect separation. Likely due to distinct features in this dataset.")
    else:
        print("Result: Model shows variance across folds, less likely to be pure overfitting.")
        
    # 5. Visualization (Pairplot)
    print("\n[CHECK 3] Visualizing Separation...")
    
    # Map back for plotting
    plot_df = X.copy()
    plot_df['Condition'] = y.map({0: 'No CKD', 1: 'CKD'})
    
    # Plot top features
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=plot_df, x='Creatinine', y='Hemoglobin', hue='Condition', style='Condition', palette='seismic', s=100)
    plt.title('Separation Check: Creatinine vs Hemoglobin')
    plt.axvline(x=1.3, color='k', linestyle='--', alpha=0.5, label='Clinical Threshold (approx 1.3)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "kidney_separation.png"))
    print(f"Saved separation plot to {os.path.join(OUTPUT_DIR, 'kidney_separation.png')}")
    plt.close()

if __name__ == "__main__":
    check_kidney_overfitting()
