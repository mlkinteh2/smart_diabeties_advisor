import pandas as pd
import numpy as np

# Set random seed for reproducibility
np.random.seed(42)

# Generate diabetes dataset
n_samples = 768

diabetes_data = {
    'Pregnancies': np.random.randint(0, 17, n_samples),
    'Glucose': np.random.randint(0, 200, n_samples),
    'BloodPressure': np.random.randint(0, 122, n_samples),
    'SkinThickness': np.random.randint(0, 100, n_samples),
    'Insulin': np.random.randint(0, 846, n_samples),
    'BMI': np.round(np.random.uniform(0, 67, n_samples), 1),
    'DiabetesPedigreeFunction': np.round(np.random.uniform(0.078, 2.42, n_samples), 3),
    'Age': np.random.randint(21, 82, n_samples),
    'Outcome': np.random.randint(0, 2, n_samples)
}

df_diabetes = pd.DataFrame(diabetes_data)
df_diabetes.to_csv('predictions/ml/diabetes.csv', index=False)
print(f"Created diabetes.csv with shape: {df_diabetes.shape}")
print(df_diabetes.head())
print("\n")

# Generate kidney dataset
n_samples_kidney = 400

kidney_data = {
    'Bp': np.random.randint(50, 180, n_samples_kidney),
    'Sg': np.round(np.random.uniform(1.005, 1.025, n_samples_kidney), 3),
    'Al': np.random.randint(0, 6, n_samples_kidney),
    'Su': np.random.randint(0, 6, n_samples_kidney),
    'Rbc': np.random.choice([0, 1], n_samples_kidney),
    'Bu': np.round(np.random.uniform(10, 180, n_samples_kidney), 1),
    'Sc': np.round(np.random.uniform(0.4, 15, n_samples_kidney), 1),
    'Sod': np.round(np.random.uniform(110, 160, n_samples_kidney), 1),
    'Pot': np.round(np.random.uniform(2.5, 7.5, n_samples_kidney), 1),
    'Hemo': np.round(np.random.uniform(3.1, 17.8, n_samples_kidney), 1),
    'Wbcc': np.random.randint(2200, 26400, n_samples_kidney),
    'Rbcc': np.round(np.random.uniform(2.1, 8.0, n_samples_kidney), 1),
    'Htn': np.random.choice([0, 1], n_samples_kidney),
    'Class': np.random.choice([0, 1], n_samples_kidney)
}

df_kidney = pd.DataFrame(kidney_data)
df_kidney.to_csv('predictions/ml/kidney.csv', index=False)
print(f"Created kidney.csv with shape: {df_kidney.shape}")
print(df_kidney.head())

print("\n✓ Both CSV files created successfully!")
