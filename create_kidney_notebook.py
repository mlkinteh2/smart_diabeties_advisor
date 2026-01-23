import json
import os

# Kidney Training Notebook
kidney_notebook = {
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# Kidney Disease Model Training, Evaluation, and Overfitting Analysis\n",
                "\n",
                "This notebook provides a comprehensive workflow for the Kidney Disease prediction system:\n",
                "1. **Training**: Evaluates 5 different machine learning algorithms.\n",
                "2. **Internal Testing**: Detailed performance metrics and confusion matrices.\n",
                "3. **Cross-Validation**: Ensuring model stability.\n",
                "4. **Overfitting Analysis**: Investigating the 100% accuracy result through correlation and learning curves.\n",
                "5. **External Validation**: Testing against the Albukhary dataset using clinical ground truth rules."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import pandas as pd\n",
                "import numpy as np\n",
                "import matplotlib.pyplot as plt\n",
                "import seaborn as sns\n",
                "from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold, learning_curve\n",
                "from sklearn.preprocessing import RobustScaler\n",
                "from sklearn.ensemble import RandomForestClassifier\n",
                "from sklearn.tree import DecisionTreeClassifier\n",
                "from sklearn.svm import SVC\n",
                "from sklearn.neighbors import KNeighborsClassifier\n",
                "from sklearn.linear_model import LogisticRegression\n",
                "from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, f1_score\n",
                "import joblib\n",
                "import os\n",
                "\n",
                "print('Libraries imported successfully!')\n",
                "sns.set_style('whitegrid')"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["## 1. Load and Preprocess UCI Dataset"]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "ML_PATH = 'predictions/ml'\n",
                "CSV_PATH = os.path.join(ML_PATH, 'kidney.csv')\n",
                "df = pd.read_csv(CSV_PATH)\n",
                "\n",
                "rename_map = {\n",
                "    'Bp': 'Blood Pressure', 'Sg': 'Specific Gravity', 'Al': 'Albumin', 'Su': 'Sugar',\n",
                "    'Rbc': 'Red Blood Cell', 'Bu': 'Urea', 'Sc': 'Creatinine', 'Sod': 'Sodium',\n",
                "    'Pot': 'Pottasium', 'Hemo': 'Hemoglobin', 'Wbcc': 'White Blood Cell Count',\n",
                "    'Rbcc': 'Red Blood Cell Count', 'Htn': 'Hypertension', 'Class': 'Predicted Class'\n",
                "}\n",
                "df.rename(columns=rename_map, inplace=True)\n",
                "\n",
                "# Feature selection\n",
                "required_cols = ['Predicted Class', 'Creatinine', 'Pottasium', 'Hemoglobin', \n",
                "                 'Sodium', 'Blood Pressure', 'Red Blood Cell', 'Urea', 'Albumin']\n",
                "df = df[required_cols]\n",
                "\n",
                "# Cleaning\n",
                "df = df[(df['Pottasium'] <= 7) & (df['Hemoglobin'] <= 20) & (df['Blood Pressure'] >= 50)]\n",
                "df['Creatinine'] = df['Creatinine'].clip(0, 15)\n",
                "df['Pottasium'] = df['Pottasium'].clip(2, 7)\n",
                "df['Hemoglobin'] = df['Hemoglobin'].clip(4, 20)\n",
                "df['Sodium'] = df['Sodium'].clip(100, 180)\n",
                "df['Blood Pressure'] = df['Blood Pressure'].clip(60, 180)\n",
                "\n",
                "X = df.drop('Predicted Class', axis=1)\n",
                "y = df['Predicted Class']\n",
                "print(f'Dataset size: {len(df)}')\n",
                "print(f'Features: {X.columns.tolist()}')"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["## 2. Overfitting Investigation: Correlation & Separation"]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "print(\"Checking for Data Leakage via Feature Correlation...\")\n",
                "corr_matrix = df.corr()\n",
                "target_corr = corr_matrix['Predicted Class'].sort_values(ascending=False)\n",
                "print(\"Correlations with Condition:\")\n",
                "print(target_corr)\n",
                "\n",
                "print(\"\\nVisualizing Feature Separation (Creatinine vs Hemoglobin)... \")\n",
                "plt.figure(figsize=(10, 6))\n",
                "sns.scatterplot(data=df, x='Creatinine', y='Hemoglobin', hue='Predicted Class', palette='seismic', s=80)\n",
                "plt.title('Separation Check: Kidney Condition Clusters')\n",
                "plt.show()\n",
                "print(\"Notice the very clear separation. Medical datasets often have sharp thresholds (e.g. Creatinine > 1.3 usually indicates CKD).\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["## 3. Train-Test Split and Scaling"]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=15)\n",
                "scaler = RobustScaler()\n",
                "X_train_scaled = scaler.fit_transform(X_train)\n",
                "X_test_scaled = scaler.transform(X_test)\n",
                "print(f'Train size: {len(X_train)}, Test size: {len(X_test)}')"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["## 4. Algorithm Comparison and Cross-Validation"]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "models = {\n",
                "    'Logistic Regression': LogisticRegression(random_state=42),\n",
                "    'K-Nearest Neighbors': KNeighborsClassifier(n_neighbors=3),\n",
                "    'Decision Tree': DecisionTreeClassifier(random_state=42),\n",
                "    'Random Forest': RandomForestClassifier(random_state=42),\n",
                "    'Support Vector Machine': SVC(random_state=42, probability=True),\n",
                "}\n",
                "\n",
                "print('Running 5-Fold Cross-Validation...')\n",
                "for name, model in models.items():\n",
                "    scores = cross_val_score(model, X_train_scaled, y_train, cv=5)\n",
                "    print(f'{name}: {scores.mean():.4f}')\n",
                "\n",
                "print('\\nTesting on Hold-out Set...')\n",
                "test_results = {}\n",
                "for name, model in models.items():\n",
                "    model.fit(X_train_scaled, y_train)\n",
                "    y_pred = model.predict(X_test_scaled)\n",
                "    acc = accuracy_score(y_test, y_pred)\n",
                "    test_results[name] = acc\n",
                "    print(f'{name}: {acc:.4f}')"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["## 5. Learning Curves (Bias vs Variance Check)"]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "print(\"Generating Learning Curve for Random Forest...\")\n",
                "best_model_name = 'Random Forest'\n",
                "model = models[best_model_name]\n",
                "\n",
                "train_sizes, train_scores, test_scores = learning_curve(\n",
                "    model, X_train_scaled, y_train, cv=5, n_jobs=-1, \n",
                "    train_sizes=np.linspace(0.1, 1.0, 5), scoring='accuracy'\n",
                ")\n",
                "\n",
                "train_mean = np.mean(train_scores, axis=1)\n",
                "test_mean = np.mean(test_scores, axis=1)\n",
                "\n",
                "plt.figure(figsize=(10, 6))\n",
                "plt.plot(train_sizes, train_mean, 'o-', color='r', label='Training Accuracy')\n",
                "plt.plot(train_sizes, test_mean, 'o-', color='g', label='Cross-validation Accuracy')\n",
                "plt.title('Learning Curve (Random Forest)')\n",
                "plt.xlabel('Training Set Size')\n",
                "plt.ylabel('Accuracy')\n",
                "plt.legend(loc='best')\n",
                "plt.show()\n",
                "print(\"If the curves converge at a high accuracy, the model generalizes well and is NOT severely overfit.\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["## 6. Detailed Evaluation"]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "best_name = max(test_results, key=test_results.get)\n",
                "best_model = models[best_name]\n",
                "y_pred = best_model.predict(X_test_scaled)\n",
                "\n",
                "print(f'Best Model: {best_name}')\n",
                "print(classification_report(y_test, y_pred))\n",
                "\n",
                "cm = confusion_matrix(y_test, y_pred)\n",
                "plt.figure(figsize=(6,5))\n",
                "sns.heatmap(cm, annot=True, fmt='d', cmap='Reds')\n",
                "plt.title(f'Kidney Confusion Matrix - {best_name}')\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["## 7. External Validation (Albukhary Dataset)"]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "print('Loading External Albukhary Dataset...')\n",
                "try:\n",
                "    ext_df = pd.read_excel('predictions/ml/test_dataset.xlsx')\n",
                "    \n",
                "    true_labels = []\n",
                "    pred_labels = []\n",
                "    \n",
                "    for _, row in ext_df.iterrows():\n",
                "        creatinine = row['Creatnine']\n",
                "        urea = row['Urea']\n",
                "        hemoglobin = row['Hemoglobin']\n",
                "        sodium = row['Sodium']\n",
                "        potassium = row['Potassium']\n",
                "        albumin = row['Albumin']\n",
                "        rbc = row['Red blood Cell']\n",
                "        \n",
                "        #SI Unit Conversions\n",
                "        if pd.notna(creatinine) and creatinine > 20: creatinine /= 88.4\n",
                "        if pd.notna(urea): urea *= 2.8\n",
                "        \n",
                "        # Clinical Ground Truth rule\n",
                "        risk_score = 0\n",
                "        if pd.notna(creatinine) and creatinine > 1.3: risk_score += 2\n",
                "        if pd.notna(urea) and urea > 45: risk_score += 1\n",
                "        if pd.notna(hemoglobin) and hemoglobin < 12: risk_score += 1\n",
                "        true_label = \"CKD\" if risk_score >= 2 else \"No CKD\"\n",
                "        \n",
                "        bp_raw = row['Blood Pressure']\n",
                "        bp = None\n",
                "        if isinstance(bp_raw, str) and '/' in bp_raw:\n",
                "            bp = float(bp_raw.split('/')[1])\n",
                "        elif pd.notna(bp_raw):\n",
                "            bp = float(bp_raw)\n",
                "            \n",
                "        rbc_val = 0.0 if str(rbc).lower() in ['abnormal', '0'] else 1.0\n",
                "        \n",
                "        feats_valid = [creatinine, potassium, hemoglobin, sodium, bp, rbc_val, urea, albumin]\n",
                "        if not any(pd.isna(v) for v in feats_valid):\n",
                "            k_input = pd.DataFrame([feats_valid], columns=X.columns)\n",
                "            k_sc = scaler.transform(k_input)\n",
                "            ml_p = \"CKD\" if best_model.predict(k_sc)[0] == 1 else \"No CKD\"\n",
                "            \n",
                "            true_labels.append(true_label)\n",
                "            pred_labels.append(ml_p)\n",
                "            \n",
                "    print(f'External Validation Accuracy: {accuracy_score(true_labels, pred_labels):.2%}')\n",
                "    print(classification_report(true_labels, pred_labels))\n",
                "    \n",
                "except Exception as e:\n",
                "    print(f'Error: {e}')"
            ]
        }
    ],
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.12.0"}
    },
    "nbformat": 4, "nbformat_minor": 4
}

with open('train_kidney_model.ipynb', 'w') as f:
    json.dump(kidney_notebook, f, indent=2)

print('✓ Enhanced kidney notebook created.')
