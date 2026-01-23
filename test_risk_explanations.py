import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medpredict.settings')
django.setup()

from predictions.explainability import generate_clinical_explanation

def test_risk_levels():
    """Test clinical explanation for all risk levels."""
    
    # Mock SHAP results
    top_positive = [('Glucose', 0.45), ('BMI', 0.32), ('Age', 0.21)]
    top_negative = [('BloodPressure', -0.15)]
    
    print("="*60)
    print("TESTING CLINICAL EXPLANATION LOGIC")
    print("="*60)
    
    # Test LOW risk
    print("\n1. LOW RISK (Diabetes):")
    print("-" * 40)
    explanation = generate_clinical_explanation(top_positive, top_negative, "diabetes", risk_level="Low")
    print(explanation)
    
    # Test MEDIUM risk
    print("\n2. MEDIUM RISK (Diabetes):")
    print("-" * 40)
    explanation = generate_clinical_explanation(top_positive, top_negative, "diabetes", risk_level="Medium")
    print(explanation)
    
    # Test HIGH risk
    print("\n3. HIGH RISK (Kidney):")
    print("-" * 40)
    kidney_pos = [('Creatinine', 0.65), ('Urea', 0.42), ('Albumin', 0.31)]
    kidney_neg = [('Hemoglobin', -0.22), ('Sodium', -0.18)]
    explanation = generate_clinical_explanation(kidney_pos, kidney_neg, "kidney disease", risk_level="High")
    print(explanation)
    
    # Test LOW risk (Kidney)
    print("\n4. LOW RISK (Kidney - should be calm):")
    print("-" * 40)
    explanation = generate_clinical_explanation(kidney_pos, kidney_neg, "kidney disease", risk_level="Low")
    print(explanation)
    
    print("\n" + "="*60)
    print("VERIFICATION COMPLETE")
    print("="*60)
    print("\nExpected behaviors:")
    print("✓ Low risk: No features listed, calm language")
    print("✓ Medium risk: Top 2-3 features, early warning tone")
    print("✓ High risk: Top features listed, serious but controlled tone")

if __name__ == "__main__":
    test_risk_levels()
