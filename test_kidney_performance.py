"""
Comprehensive Kidney Disease Model Testing
Tests the model with realistic patient scenarios to verify prediction accuracy
"""
import pandas as pd
import numpy as np
import joblib
import os
import sys

# Force AppData path
user_site = os.path.expanduser(r"~\AppData\Roaming\Python\Python312\site-packages")
if os.path.exists(user_site) and user_site not in sys.path:
    sys.path.insert(0, user_site)

ml_dir = 'predictions/ml'

# Load the kidney model and scaler
k_model = joblib.load(os.path.join(ml_dir, 'kidney_model.pkl'))
k_scaler = joblib.load(os.path.join(ml_dir, 'kid_scaler.pkl'))

print("=" * 80)
print("KIDNEY DISEASE MODEL PERFORMANCE TEST")
print("=" * 80)
print()

# Define test scenarios
test_cases = [
    {
        "name": "Scenario 1: Healthy Young Adult",
        "description": "25-year-old with normal kidney function",
        "expected": "Low Risk",
        "values": {
            'Creatinine': 0.9,      # Normal (0.6-1.2 mg/dL)
            'Pottasium': 4.2,       # Normal (3.5-5.2 mEq/L)
            'Hemoglobin': 15.0,     # Normal (13.5-17.5 g/dL)
            'Sodium': 140.0,        # Normal (135-145 mEq/L)
            'Blood Pressure': 110,  # Normal (90-120 mmHg)
            'Red Blood Cell': 1.0,  # Normal
            'Urea': 12.0,           # Normal (7-20 mg/dL)
            'Albumin': 0.0          # Normal (0)
        }
    },
    {
        "name": "Scenario 2: Healthy Older Adult",
        "description": "65-year-old with good kidney function",
        "expected": "Low Risk",
        "values": {
            'Creatinine': 1.1,      # Normal-high
            'Pottasium': 4.0,       # Normal
            'Hemoglobin': 14.0,     # Normal
            'Sodium': 138.0,        # Normal
            'Blood Pressure': 115,  # Normal
            'Red Blood Cell': 1.0,  # Normal
            'Urea': 15.0,           # Normal
            'Albumin': 0.0          # Normal
        }
    },
    {
        "name": "Scenario 3: Borderline Case",
        "description": "Patient with slightly elevated creatinine",
        "expected": "Medium Risk",
        "values": {
            'Creatinine': 1.5,      # Slightly elevated
            'Pottasium': 4.5,       # Normal
            'Hemoglobin': 12.5,     # Slightly low
            'Sodium': 136.0,        # Normal
            'Blood Pressure': 125,  # Slightly elevated
            'Red Blood Cell': 1.0,  # Normal
            'Urea': 22.0,           # Slightly elevated
            'Albumin': 0.0          # Normal
        }
    },
    {
        "name": "Scenario 4: Moderate Kidney Disease",
        "description": "Patient with clear kidney impairment",
        "expected": "High Risk",
        "values": {
            'Creatinine': 2.5,      # Elevated
            'Pottasium': 5.5,       # Elevated
            'Hemoglobin': 10.0,     # Low (anemia)
            'Sodium': 132.0,        # Low
            'Blood Pressure': 140,  # Elevated
            'Red Blood Cell': 0.0,  # Abnormal
            'Urea': 45.0,           # Elevated
            'Albumin': 1.0          # Trace protein
        }
    },
    {
        "name": "Scenario 5: Severe Kidney Disease",
        "description": "Patient with advanced kidney failure",
        "expected": "High Risk",
        "values": {
            'Creatinine': 5.0,      # Very high
            'Pottasium': 6.2,       # Very high
            'Hemoglobin': 8.0,      # Very low (severe anemia)
            'Sodium': 128.0,        # Low
            'Blood Pressure': 160,  # Very high
            'Red Blood Cell': 0.0,  # Abnormal
            'Urea': 80.0,           # Very high
            'Albumin': 2.0          # Significant proteinuria
        }
    },
    {
        "name": "Scenario 6: Athletic Individual",
        "description": "Muscular athlete with slightly higher creatinine",
        "expected": "Low Risk",
        "values": {
            'Creatinine': 1.3,      # Higher due to muscle mass
            'Pottasium': 4.3,       # Normal
            'Hemoglobin': 16.5,     # High-normal (athletic)
            'Sodium': 141.0,        # Normal
            'Blood Pressure': 105,  # Low-normal (athletic)
            'Red Blood Cell': 1.0,  # Normal
            'Urea': 14.0,           # Normal
            'Albumin': 0.0          # Normal
        }
    }
]

# Run tests
results = []
for i, test in enumerate(test_cases, 1):
    print(f"\n{'─' * 80}")
    print(f"TEST {i}: {test['name']}")
    print(f"{'─' * 80}")
    print(f"Description: {test['description']}")
    print(f"Expected Risk: {test['expected']}")
    print()
    
    # Display input values
    print("Input Values:")
    for key, value in test['values'].items():
        print(f"  {key:20s}: {value}")
    
    # Create DataFrame with correct column order
    test_df = pd.DataFrame([test['values']])
    
    # Scale and predict
    test_scaled = k_scaler.transform(test_df)
    probability = k_model.predict_proba(test_scaled)[0][1] * 100
    
    # Determine risk level
    if probability < 30:
        risk_level = "Low Risk"
    elif probability < 70:
        risk_level = "Medium Risk"
    else:
        risk_level = "High Risk"
    
    # Check if prediction matches expectation
    match = "✓ PASS" if risk_level == test['expected'] else "✗ FAIL"
    
    print()
    print(f"Prediction Results:")
    print(f"  Disease Probability: {probability:.1f}%")
    print(f"  Risk Level: {risk_level}")
    print(f"  Test Result: {match}")
    
    results.append({
        'scenario': test['name'],
        'expected': test['expected'],
        'predicted': risk_level,
        'probability': probability,
        'passed': risk_level == test['expected']
    })

# Summary
print(f"\n{'=' * 80}")
print("TEST SUMMARY")
print(f"{'=' * 80}")
print()

passed = sum(1 for r in results if r['passed'])
total = len(results)
accuracy = (passed / total) * 100

print(f"Tests Passed: {passed}/{total} ({accuracy:.1f}%)")
print()

print("Detailed Results:")
print(f"{'Scenario':<40} {'Expected':<15} {'Predicted':<15} {'Prob':<10} {'Result'}")
print("─" * 90)
for r in results:
    result_icon = "✓" if r['passed'] else "✗"
    print(f"{r['scenario']:<40} {r['expected']:<15} {r['predicted']:<15} {r['probability']:>6.1f}%   {result_icon}")

print()
print("=" * 80)
print("CONCLUSION:")
if accuracy >= 80:
    print("✓ Model is performing WELL - predictions align with clinical expectations")
elif accuracy >= 60:
    print("⚠ Model is performing MODERATELY - some predictions need review")
else:
    print("✗ Model needs IMPROVEMENT - predictions do not align with expectations")
print("=" * 80)
