import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medpredict.settings')
django.setup()

from predictions.models import Prediction, Patient
from django.contrib.auth.models import User
from recommendations.engine import generate_recommendation

# Get a recent prediction
try:
    pred = Prediction.objects.latest('created_at')
    print(f"Testing with Prediction ID: {pred.id}")
    print(f"Diabetes Risk: {pred.diabetes_risk}, Kidney Risk: {pred.kidney_risk}")
    
    # Prepare features dict
    features = {
        'Age': 45,
        'BMI': 28,
        'Glucose': 120,
        'BP_Systolic': 120,
        'Creatinine': 1.0,
        'Pottasium': 4.5,
        'Hemoglobin': 13,
        'Sodium': 140,
        'Urea': 30,
        'Albumin': 0
    }
    
    print("\n--- Calling generate_recommendation ---")
    full_text, d_summary, k_summary = generate_recommendation(pred, features, shap_summary=None)
    
    print("\n✓ SUCCESS: Recommendation generated")
    print(f"Length of full_text: {len(full_text)} characters")
    print(f"Diabetes summary: {d_summary}")
    print(f"Kidney summary: {k_summary}")
    
    # Check if HTML is valid
    if '<div' in full_text and '</div>' in full_text:
        print("✓ HTML structure appears valid")
    else:
        print("⚠ WARNING: HTML structure may be incomplete")
        
except Exception as e:
    print(f"✗ ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
