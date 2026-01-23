import json
import os

# Diabetes Training Notebook
diabetes_notebook = {
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# Diabetes Model Training, Evaluation, and External Validation\n",
                "\n",
                "This notebook provides a comprehensive workflow for the Diabetes prediction system:\n",
                "1. **Training**: Evaluates 5 different machine learning algorithms.\n",
                "2. **Internal Testing**: Detailed performance metrics and confusion matrices.\n",
                "3. **Cross-Validation**: Ensuring model robustness.\n",
                "4. **External Validation**: Testing against the Albukhary dataset."
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
                "from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold\n",
                "from sklearn.preprocessing import RobustScaler\n",
                "from sklearn.ensemble import RandomForestClassifier\n",
                "from sklearn.tree import DecisionTreeClassifier\n",
                "from sklearn.svm import SVC\n",
                "from sklearn.neighbors import KNeighborsClassifier\n",
                "from sklearn.linear_model import LogisticRegression\n",
                "from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, f1_score\n",
                "from imblearn.over_sampling import SMOTE\n",
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
            "source": ["## 1. Load and Clean Dataset"]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "ML_PATH = 'predictions/ml'\n",
                "CSV_PATH = os.path.join(ML_PATH, 'diabetes.csv')\n",
                "\n",
                "df = pd.read_csv(CSV_PATH)\n",
                "print(f'Dataset shape: {df.shape}')\n",
                "\n",
                "# Impute zero values with median\n",
                "zero_impute_cols = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']\n",
                "for col in zero_impute_cols:\n",
                "    if col in df.columns:\n",
                "        median_val = df[df[col] != 0][col].median()\n",
                "        df[col] = df[col].replace(0, median_val)\n",
                "\n",
                "# Select core features\n",
                "df = df[['Age', 'BMI', 'BloodPressure', 'Glucose', 'Outcome']]\n",
                "X = df.drop('Outcome', axis=1)\n",
                "y = df['Outcome']\n",
                "print(f'Using features: {X.columns.tolist()}')"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["## 2. Train-Test Split and Class Balancing"]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=15)\n",
                "\n",
                "# Apply SMOTE\n",
                "sm = SMOTE(random_state=42)\n",
                "X_train_res, y_train_res = sm.fit_resample(X_train, y_train)\n",
                "\n",
                "# Scaling\n",
                "scaler = RobustScaler()\n",
                "X_train_scaled = scaler.fit_transform(X_train_res)\n",
                "X_test_scaled = scaler.transform(X_test)\n",
                "\n",
                "print(f'Original Class Dist: {y_train.value_counts().to_dict()}')\n",
                "print(f'Balanced Class Dist: {y_train_res.value_counts().to_dict()}')"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["## 3. Algorithm Comparison and Cross-Validation"]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "models = {\n",
                "    'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),\n",
                "    'K-Nearest Neighbors': KNeighborsClassifier(n_neighbors=3),\n",
                "    'Decision Tree': DecisionTreeClassifier(random_state=42),\n",
                "    'Random Forest': RandomForestClassifier(random_state=42),\n",
                "    'Support Vector Machine': SVC(random_state=42, probability=True),\n",
                "}\n",
                "\n",
                "print('Running 5-Fold Cross-Validation...')\n",
                "cv_results = {}\n",
                "for name, model in models.items():\n",
                "    scores = cross_val_score(model, X_train_scaled, y_train_res, cv=5)\n",
                "    cv_results[name] = scores.mean()\n",
                "    print(f'{name}: {scores.mean():.4f}')\n",
                "\n",
                "print('\\nTesting on Hold-out Set...')\n",
                "test_results = {}\n",
                "for name, model in models.items():\n",
                "    model.fit(X_train_scaled, y_train_res)\n",
                "    y_pred = model.predict(X_test_scaled)\n",
                "    acc = accuracy_score(y_test, y_pred)\n",
                "    test_results[name] = acc\n",
                "    print(f'{name}: {acc:.4f}')"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["## 4. Evaluation (Confusion Matrices)"]
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
                "sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')\n",
                "plt.title(f'Diabetes Confusion Matrix - {best_name}')\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["## 5. External Validation (Albukhary Dataset)"]
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
                "    print(f'Loaded {len(ext_df)} rows.')\n",
                "    \n",
                "    true_labels = []\n",
                "    pred_labels = []\n",
                "    \n",
                "    for _, row in ext_df.iterrows():\n",
                "        glucose = row['Glucose']\n",
                "        age = row['Age']\n",
                "        bmi = row['BMI']\n",
                "        \n",
                "        # Unit Conversion Heuristic\n",
                "        if pd.notna(glucose) and glucose < 50:\n",
                "            glucose = glucose * 18.0182\n",
                "            \n",
                "        # Clinical Ground Truth Assumption\n",
                "        clinical_truth = \"Positive\" if glucose >= 140 else \"Negative\"\n",
                "        \n",
                "        # BP Extraction\n",
                "        bp_raw = row['Blood Pressure']\n",
                "        bp = None\n",
                "        if isinstance(bp_raw, str) and '/' in bp_raw:\n",
                "            bp = float(bp_raw.split('/')[1])\n",
                "        elif pd.notna(bp_raw): bp = float(bp_raw)\n",
                "        \n",
                "        if not any(pd.isna([age, bmi, bp, glucose])):\n",
                "            # ML Prediction\n",
                "            feat = np.array([[age, bmi, bp, glucose]])\n",
                "            feat_sc = scaler.transform(feat)\n",
                "            ml_pred = \"Positive\" if best_model.predict(feat_sc)[0] == 1 else \"Negative\"\n",
                "            \n",
                "            true_labels.append(clinical_truth)\n",
                "            pred_labels.append(ml_pred)\n",
                "            \n",
                "    print('\\nExternal Validation Metrics (Albukhary):')\n",
                "    print(f'Accuracy: {accuracy_score(true_labels, pred_labels):.2%}')\n",
                "    print(classification_report(true_labels, pred_labels))\n",
                "    \n",
                "except Exception as e:\n",
                "    print(f'Could not run external validation: {e}')"
            ]
        }
    ],
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.12.0"}
    },
    "nbformat": 4, "nbformat_minor": 4
}

with open('train_diabetes_model.ipynb', 'w') as f:
    json.dump(diabetes_notebook, f, indent=2)

print('✓ Enhanced diabetes notebook created.')
