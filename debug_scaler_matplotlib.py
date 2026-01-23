import os
import joblib
import pandas as pd
import sklearn
import sys

# Setup Django environment to use settings if needed, but we can just load files directly
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ML_PATH = os.path.join(BASE_DIR, "predictions/ml")
SCALER_PATH = os.path.join(ML_PATH, "kid_scaler.pkl")

print(f"Sklearn version: {sklearn.__version__}")

# 1. Check Scaler Feature Names
try:
    print(f"Loading scaler from: {SCALER_PATH}")
    scaler = joblib.load(SCALER_PATH)
    print(f"Scaler type: {type(scaler)}")
    
    if hasattr(scaler, "feature_names_in_"):
        print("Scaler has feature_names_in_:")
        print(scaler.feature_names_in_)
    else:
        print("Scaler does NOT have feature_names_in_")
        
except Exception as e:
    print(f"Error loading scaler: {e}")

# 2. Test Matplotlib
print("\nTesting Matplotlib...")
try:
    import matplotlib
    print(f"Matplotlib imported. Type: {type(matplotlib)}")
    
    if hasattr(matplotlib, '__file__'):
        print(f"Matplotlib file: {matplotlib.__file__}")
    else:
        print("Matplotlib has no __file__ attribute")
        
    if hasattr(matplotlib, '__path__'):
        print(f"Matplotlib path: {matplotlib.__path__}")
        
    print(f"Dir(matplotlib): {dir(matplotlib)[:20]}...") # Print first 20 items
    
    if hasattr(matplotlib, 'use'):
        print("matplotlib.use exists")
        matplotlib.use('Agg')
        print("matplotlib.use('Agg') successful")
    else:
        print("matplotlib.use does NOT exist")

    import matplotlib.pyplot as plt
    print("matplotlib.pyplot imported successfully")
    
except Exception as e:
    print(f"Error testing matplotlib: {e}")
    import traceback
    traceback.print_exc()
