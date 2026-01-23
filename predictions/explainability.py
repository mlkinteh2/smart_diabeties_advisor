import os
import matplotlib
matplotlib.use('Agg')  # Force Agg backend before importing pyplot
import matplotlib.pyplot as plt
import shap
import numpy as np
import joblib
from pathlib import Path
from django.conf import settings

# Ensure output directory exists
EXPLAIN_DIR = Path(settings.MEDIA_ROOT) / "explain"
EXPLAIN_DIR.mkdir(parents=True, exist_ok=True)

def generate_global_feature_importance(model, feature_names, model_name, background_data=None):
    """
    Generate and save global feature importance plot for the model.
    This is generated ONCE and reused.
    
    Args:
        model: Trained model object
        feature_names: List of feature names
        model_name: 'diabetes' or 'kidney'
        background_data: Optional DataFrame or numpy array for SHAP background (required for SVM)
        
    Returns:
        str: Relative path to the saved image
    """
    filename = f"global_{model_name}_fi.png"
    filepath = EXPLAIN_DIR / filename
    
    # If file exists, return existing path (reuse)
    # Check if file exists and ensure it's not empty/corrupt (basic check)
    if filepath.exists() and filepath.stat().st_size > 0:
        return f"explain/{filename}"
    
    try:
        importance = None
        
        # 1. Try native feature importance (Trees)
        try:
            if hasattr(model, 'feature_importances_'):
                importance = model.feature_importances_
        except Exception:
            pass
            
        if importance is None:
            # 2. Try coefficients (Linear)
            try:
                # Safe check for coef_ which might raise errors on some SVM configurations
                if hasattr(model, 'coef_'):
                    if model.coef_.ndim > 1:
                        importance = np.abs(model.coef_[0])
                    else:
                        importance = np.abs(model.coef_)
            except Exception:
                pass
                
        # 3. Fallback: SHAP-based Global Importance (SVM / RBF)
        if importance is None and background_data is not None:
            print(f"Calculating SHAP-based Global FI for {model_name}...")
            # Use summarized background data to speed up KernelExplainer
            # K-means summary of 10-20 samples is usually sufficient for global trend
            try:
                # Ensure numpy array
                X_bg = np.asarray(background_data, dtype=np.float64)
                
                # Summarize usually helpful for large datasets, but if passed small sample, use directly
                # To avoid potential ambiguity errors with shap.kmeans objects, we'll use a direct subsample
                if len(X_bg) > 10:
                    # Random sample or just first 10
                    # Using first 10 for deterministic behavior if not shuffled, or simple logic
                    X_summary = X_bg[:10]
                else:
                    X_summary = X_bg
                
                # Setup Explainer
                # For SVM, we need a generic explainer (Kernel) working on the predict function
                # Note: model.predict might return classes or probabilities. KernelExplainer usually likes predict_proba for better granularity,
                # but for importance, predict is often okay if discrete. Ideally probability.
                fn = model.predict_proba if hasattr(model, 'predict_proba') else model.predict
                
                explainer = shap.KernelExplainer(fn, X_summary)
                
                # Calculate SHAP values for a representative sample (e.g., the summary itself or a subset of background)
                # Ideally we want the average magnitude over the dataset
                shap_values = explainer.shap_values(X_summary)
                
                # Handle SHAP output shape
                if isinstance(shap_values, list):
                    shap_values = shap_values[1] # Positive class
                
                # Compute global importance: mean absolute value per feature
                importance = np.mean(np.abs(shap_values), axis=0)
                
            except Exception as e:
                print(f"SHAP Global FI calculation failed for {model_name}: {e}")
                import traceback
                traceback.print_exc()
                return None
        
        if importance is None:
            print(f"Warning: Could not extract global importance for {model_name}")
            return None

        # Ensure 1D
        if hasattr(importance, 'flatten'):
            importance = importance.flatten()
        
        # Sort and plot
        fig = plt.figure(figsize=(10, 6))
        
        indices = np.argsort(importance)[::-1][:10]  # Top 10
        valid_indices = [i for i in indices if i < len(feature_names)]
        
        plt.barh([feature_names[i] for i in valid_indices], importance[valid_indices], color='#2563eb')
        plt.xlabel("Relative Importance (SHAP impact if applicable)", fontsize=12, fontweight='bold')
        plt.title(f"{model_name.capitalize()} - Global Feature Importance", fontsize=14, fontweight='bold')
        plt.gca().invert_yaxis()
        plt.tight_layout()
        
        fig.savefig(filepath, dpi=100, bbox_inches='tight')
        plt.close(fig)
        
        return f"explain/{filename}"
        
    except Exception as e:
        print(f"Error generating global FI for {model_name}: {e}")
        return None

def generate_clinical_explanation(top_positive, top_negative, condition_name, risk_level="Low"):
    """
    Generate plain-English clinical explanation based on risk level.
    """
    parts = []
    
    # 1. LOW RISK - Calm, no features listed
    if risk_level == "Low":
        return "Values are within acceptable clinical limits. No significant pathological drivers detected."
        
    # 2. MEDIUM RISK - Early warning, top 2-3 features
    if risk_level == "Medium":
        if top_positive:
            features = [name for name, _ in top_positive]
            # Take top 3 max
            features = features[:3]
            feature_str = ", ".join(features)
            parts.append(f"Early clinical changes observed in: {feature_str}.")
        else:
            parts.append("Moderate risk factors detected, warranting observation.")
            
    # 3. HIGH RISK - Serious, top features
    elif risk_level == "High":
        if top_positive:
            features = [name for name, _ in top_positive]
            feature_str = ", ".join(features)
            parts.append(f"Significant clinical contribution from: {feature_str}.")
        else:
            parts.append("Clinical data indicates elevated risk profile.")
            
    # Add protective factors if relevant (mostly for High/Medium to show balance)
    if top_negative and risk_level in ["Medium", "High"]:
        features = [name for name, _ in top_negative]
        feature_str = ", ".join(features[:2]) # Just top 2 protective
        parts.append(f"Protective factors noted: {feature_str}.")
        
    return " ".join(parts)

def generate_patient_shap(model, scaler, input_data, feature_names, prediction_id, model_name, risk_level="Low", background_data=None):
    """
    Generate SHAP force/waterfall plot and clinical explanation.
    """
    filename = f"shap_{model_name}_{prediction_id}.png"
    filepath = EXPLAIN_DIR / filename
    
    explanation_text = "Analysis not available."
    
    try:
        # 1. Scale Data
        X_raw = np.asarray(input_data, dtype=np.float64)
        if X_raw.ndim == 1:
            X_raw = X_raw.reshape(1, -1)
            
        X_scaled = scaler.transform(X_raw)
        
        # 2. Compute SHAP Values
        explainer = None
        shap_values = None
        
        # Use simple background (zeros) if none provided, but try to use provided one
        if background_data is None:
            # Fallback to zero (median for RobustScaler)
            # Use a small shape (1, features)
            masker_data = np.zeros_like(X_scaled) 
        else:
            masker_data = background_data

        # Select Explainer
        try:
            # Tree-based
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(X_scaled)
        except:
            try:
                # Linear
                # LinearExplainer requires a background (masker) to determine baseline.
                # If we pass X_scaled (the input itself), SHAP values will be 0.
                explainer = shap.LinearExplainer(model, masker_data)
                shap_values = explainer.shap_values(X_scaled)
            except:
                try:
                    # Fallback (Kernel)
                    explainer = shap.KernelExplainer(model.predict, masker_data)
                    shap_values = explainer.shap_values(X_scaled)
                except Exception as e:
                    print(f"SHAP Explainer failed for {model_name}: {e}")
                    return None, explanation_text

        # Handle SHAP output shape
        vals = shap_values
        if isinstance(shap_values, list):
            vals = shap_values[1][0]
        elif shap_values.ndim == 3:
            # (Samples, Features, Classes) -> Sample 0, Class 1
            vals = shap_values[0, :, 1]
        elif shap_values.ndim == 2:
            vals = shap_values[0]
            
        base_value = explainer.expected_value
        if isinstance(base_value, list) or isinstance(base_value, np.ndarray):
             if len(base_value) > 1:
                 base_value = base_value[1]
             else:
                 base_value = base_value[0]
        
        # 3. Generate Plot
        plt.close('all')
        
        try:
             # Use Bar Plot for better clarity (Force plot can be messy for static images)
             plt.figure(figsize=(12, 7))
             shap.bar_plot(vals, feature_names=feature_names, show=False)
             
             # Add clarifying title
             plt.title(f"{model_name.capitalize()} - Patient Specific Factors\n" + 
                      "Red = Increases Disease Risk | Blue = Decreases Disease Risk", 
                      fontsize=13, fontweight='bold', pad=15)
             plt.xlabel("SHAP value (impact on model output)", fontsize=11)
             
             plt.savefig(filepath, bbox_inches='tight', dpi=100)
        except Exception as e:
             print(f"Primary plot failed: {e}")
             # Fallback to simple plot if SHAP bar fails
             plt.close('all')
             fig, ax = plt.subplots(figsize=(10, 6))
             y_pos = np.arange(len(feature_names))
             ax.barh(y_pos, vals)
             ax.set_yticks(y_pos)
             ax.set_yticklabels(feature_names)
             ax.invert_yaxis()
             ax.set_xlabel("SHAP Value")
             plt.savefig(filepath, bbox_inches='tight')

        plt.close('all')
        
        # 4. Generate Text Explanation
        feature_impacts = zip(feature_names, vals)
        sorted_impacts = sorted(feature_impacts, key=lambda x: x[1], reverse=True) # Descending (Positive first)
        
        # Top 3 Positive (Risk Increasing)
        top_positive = [(n, v) for n, v in sorted_impacts if v > 0][:3]
        
        # Top 3 Negative (Protective) - sorted explicitly ascending to get most negative
        sorted_by_val = sorted(zip(feature_names, vals), key=lambda x: x[1])
        top_negative = [(n, v) for n, v in sorted_by_val if v < 0][:3]
        
        condition = "diabetes" if model_name == 'diabetes' else "kidney disease"
        explanation_text = generate_clinical_explanation(top_positive, top_negative, condition, risk_level)
            
        return f"explain/{filename}", explanation_text, {'top_positive': [n for n,v in top_positive], 'top_negative': [n for n,v in top_negative]}

    except Exception as e:
        print(f"Error generating patient SHAP for {model_name}: {e}")
        import traceback
        traceback.print_exc()
        return None, explanation_text, {}
