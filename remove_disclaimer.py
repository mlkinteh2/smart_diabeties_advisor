import os
import django
import sys

# Setup Django environment
sys.path.append('d:/Projects/Final_Project/medpredict')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medpredict.settings')
django.setup()

from predictions.models import Prediction

def remove_disclaimer():
    disclaimer_html = """
    <div class="alert alert-primary d-flex align-items-center mb-4" role="alert">
        <i class="bi bi-info-circle-fill fs-4 me-3"></i>
        <div>
            <strong>Important Information</strong><br>
            These recommendations are personalized based on your risk assessment results. Please consult with your healthcare provider before making significant changes to your diet, exercise routine, or medications.
        </div>
    </div>
    """
    
    # Normalize whitespace for matching/replacing
    disclaimer_html_stripped = "".join(line.strip() for line in disclaimer_html.splitlines())
    
    count = 0
    predictions = Prediction.objects.exclude(recommendation_text__isnull=True).exclude(recommendation_text='')
    
    print(f"Checking {predictions.count()} predictions...")
    
    for prediction in predictions:
        original_text = prediction.recommendation_text
        
        # We try to remove the exact string, but whitespace might vary. 
        # A simpler approach for this specific large block is to replace it if it's there.
        # Since I copied the string exactly from utils.py, it should match if stored verbatim.
        # However, newlines/indentation might differ in storage vs string literal.
        
        if "Important Information" in original_text:
            # Safe approach: Remove the div block using string manipulation
            # We look for the start and end of the alert div
            start_marker = '<div class="alert alert-primary d-flex align-items-center mb-4" role="alert">'
            end_marker = '</div>\n    </div>'
            
            # Since exact matching is brittle, let's try a split/join or specific substring replacement based on key phrase
            # If we just remove the specific text content, the empty div might remain.
            # But the user specifically asked to remove the sentence.
            
            # Let's try replacing the known block first.
            new_text = original_text.replace(disclaimer_html.strip(), "")
            
            # If that didn't work (due to whitespace), try a more aggressive approach
            if new_text == original_text:
                # Fallback: Remove lines containing the text
                lines = original_text.splitlines()
                new_lines = []
                skip = False
                for line in lines:
                    if 'Important Information' in line:
                        skip = True # Start skipping logic if multiline, but here it's inside a div
                        # Actually, better to just reconstruct without that alert.
                        pass
                    elif 'These recommendations are personalized' in line:
                        pass
                    elif 'consult with your healthcare provider' in line:
                        pass
                    elif '<div class="alert alert-primary' in line and 'Important Information' in original_text:
                        # This is risky if there are other primary alerts.
                        # But in this app, this is likely the only one in recommendations.
                        pass 
                    else:
                        new_lines.append(line)
                
                # Given the structure, maybe just replacing the specific HTML structure found in utils.py
                # Let's try to match the exact content from previous utils.py view
                
                target_string = """<div class="alert alert-primary d-flex align-items-center mb-4" role="alert">
        <i class="bi bi-info-circle-fill fs-4 me-3"></i>
        <div>
            <strong>Important Information</strong><br>
            These recommendations are personalized based on your risk assessment results. Please consult with your healthcare provider before making significant changes to your diet, exercise routine, or medications.
        </div>
    </div>"""
                
                # Check if doing a whitespace-insensitive replace helps
                # This is a bit complex to script perfectly without regex.
                pass

    # RE-STRATEGY: Use regex to remove the specific div block
    import re
    
    pattern = re.compile(r'<div class="alert alert-primary.*?Important Information.*?</div>\s*</div>', re.DOTALL)
    
    for prediction in predictions:
        if "Important Information" in prediction.recommendation_text:
            new_text = pattern.sub('', prediction.recommendation_text)
            
            if new_text != prediction.recommendation_text:
                prediction.recommendation_text = new_text
                prediction.save()
                count += 1
                
    print(f"Updated {count} predictions.")

if __name__ == "__main__":
    remove_disclaimer()
