
import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medpredict.settings')
django.setup()

from predictions.models import Prediction
from predictions.utils import generate_recommendation

def update_all_recommendations():
    print("Starting recommendation update...")
    predictions = Prediction.objects.all()
    count = 0
    for pred in predictions:
        print(f"Updating prediction {pred.id} (Risk: {pred.diabetes_risk}/{pred.kidney_risk})")
        
        # Generate new HTML content
        new_html = generate_recommendation(pred.diabetes_risk, pred.kidney_risk)
        
        # Update specific fields based on model structure
        # (Assuming recommendation_text is a field on Prediction or related model)
        if hasattr(pred, 'recommendation_text'):
            pred.recommendation_text = new_html
            pred.save()
            print("  Updated prediction.recommendation_text")
            
        # Also check related Recommendation object if it exists
        if hasattr(pred, 'recommendation') and pred.recommendation:
            pred.recommendation.text = new_html
            pred.recommendation.save()
            print("  Updated related recommendation.text")
            
        count += 1
    
    print(f"Successfully updated {count} predictions with new HTML layout.")

if __name__ == "__main__":
    update_all_recommendations()
