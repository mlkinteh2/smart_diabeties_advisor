import pandas as pd

# Read the downloaded data (no headers)
df = pd.read_csv('predictions/ml/diabetes.csv', header=None)

# Add proper column names
df.columns = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 
              'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age', 'Outcome']

# Save with headers
df.to_csv('predictions/ml/diabetes.csv', index=False)
print(f"Diabetes dataset prepared: {df.shape}")
print(df.head())
