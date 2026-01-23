"""
Utility functions for ML predictions and explainability
"""
import os
import numpy as np
import joblib
from django.conf import settings
from pathlib import Path


def load_models():
    """Load both diabetes and kidney disease models and their scalers"""
    ml_path = os.path.join(settings.BASE_DIR, "predictions/ml")
    
    diabetes_model = joblib.load(os.path.join(ml_path, "diabetes_model.pkl"))
    diabetes_scaler = joblib.load(os.path.join(ml_path, "diab_scaler.pkl"))
    
    kidney_model = joblib.load(os.path.join(ml_path, "kidney_model.pkl"))
    kidney_scaler = joblib.load(os.path.join(ml_path, "kid_scaler.pkl"))
    
    return diabetes_model, diabetes_scaler, kidney_model, kidney_scaler


def calculate_risk_level(probability):
    """Calculate risk level from probability"""
    if probability < 0.3:
        return "Low"
    elif probability < 0.7:
        return "Medium"
    else:
        return "High"


# generate_explainability removed - functionality moved to explainability.py



