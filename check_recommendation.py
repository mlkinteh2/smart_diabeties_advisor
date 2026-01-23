import os
import django
import sys

# Setup Django environment
sys.path.append('d:/Projects/Final_Project/medpredict')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medpredict.settings')
django.setup()

from predictions.models import Prediction

def check_latest_prediction():
    # Get the most recent prediction
    prediction = Prediction.objects.first()
    if prediction:
        print(f"Prediction ID: {prediction.id}")
        print("Raw Recommendation Text (first 500 chars):")
        print(prediction.recommendation_text[:500])
        
        if "&lt;" in prediction.recommendation_text:
            print("\nWARNING: HTML Entities found! Content is escaped.")
        else:
            print("\nContent looks like raw HTML (correct).")
    else:
        print("No predictions found.")

if __name__ == "__main__":
    check_latest_prediction()
