import numpy as np
from datetime import date

def calculate_egfr(creatinine, age, gender):
    """
    Calculate eGFR using CKD-EPI 2021 (Race-free) equation.
    """
    try:
        scr = float(creatinine)
        age = float(age)
        
        if gender.lower().startswith('f'):
            kappa = 0.7
            alpha = -0.329
            gender_factor = 1.012
        else:
            kappa = 0.9
            alpha = -0.411
            gender_factor = 1.0
            
        # eGFR calc expects Creatinine in mg/dL usually.
        # Input is already in mg/dL from the form.
        scr_mg = scr
        
        egfr = 142 * ((min(scr_mg / kappa, 1)) ** alpha) * \
               ((max(scr_mg / kappa, 1)) ** -1.200) * \
               (0.9938 ** age) * gender_factor
               
        return round(egfr, 1)
    except Exception:
        return None

def validate_clamp(value, min_val, max_val):
    """Clamp values to biologically plausible ranges."""
    try:
        val = float(value)
        return max(min_val, min(val, max_val))
    except (ValueError, TypeError):
        return min_val

def generate_recommendation(prediction, features, shap_summary=None):
    """
    Generate clinically relevant, user-friendly recommendations.
    """
    
    # --- 1. DATA PREPARATION & VALIDATION ---
    age = validate_clamp(features.get('Age', prediction.patient.age or 50), 18, 100)
    bmi = validate_clamp(features.get('BMI', 0), 10, 60)
    glucose = validate_clamp(features.get('Glucose', 0), 0, 600) # mg/dL
    bp_sys = validate_clamp(features.get('BP_Systolic', 120), 0, 250)
    
    # Kidney specific
    creatinine = validate_clamp(features.get('Creatinine', 1.0), 0, 20) # mg/dL
    potassium = validate_clamp(features.get('Pottasium', 0), 0, 10)
    sodium = validate_clamp(features.get('Sodium', 0), 0, 200)
    
    # Calculate eGFR
    gender = prediction.patient.gender if hasattr(prediction.patient, 'gender') else 'Male'
    egfr = calculate_egfr(creatinine, age, gender)
    
    # --- 2. RISK ANALYSIS ---
    d_risk = prediction.diabetes_risk
    k_risk = prediction.kidney_risk
    
    # --- 3. GENERATE RECOMMENDATION TEXT ---
    sections = []
    
    # Helper for risk badges
    def get_badge(risk):
        if risk == "High": return "bg-danger"
        if risk == "Medium": return "bg-warning text-dark"
        return "bg-success"
        
    d_badge = get_badge(d_risk)
    k_badge = get_badge(k_risk)
    
    # SECTION 1: CONDITION SUMMARY (Contextual)
    condition_text = ""
    
    if d_risk == "Low" and k_risk == "Low":
        condition_text = "Your results show normal kidney function and low diabetes risk."
    elif d_risk == "Medium" and k_risk == "Low":
        condition_text = "Early changes suggest increased diabetes risk, while kidney function remains stable."
    elif d_risk == "High" and k_risk == "Low":
        condition_text = "High diabetes risk may affect long-term kidney health if unmanaged."
    elif d_risk == "Low" and k_risk == "Medium":
        condition_text = "Kidney function is reduced but not at dialysis stage."
    elif d_risk == "Low" and k_risk == "High":
        if egfr and egfr < 15:
            condition_text = "Advanced kidney disease requires specialized dialysis-aware care."
        else:
            condition_text = "Advanced kidney disease requires specialized pre-dialysis care."
    elif d_risk == "High" and k_risk == "High":
        condition_text = "This combination requires close medical supervision from both kidney and diabetes specialists."
    else:
        # Mixed cases
        condition_text = "Your results indicate multiple areas requiring clinical attention."
    
    summary_html = f"""
    <div class="mb-4">
        <h5 class="mb-2 border-bottom pb-2"><i class="bi bi-clipboard2-pulse me-2"></i>Condition Summary</h5>
        <p class="mb-0">{condition_text}</p>
    </div>
    """
    sections.append(summary_html)
    
    # SECTION 3: DAILY DIET GUIDANCE / LIFESTYLE
    diet_items = []
    
    if d_risk == "Low" and k_risk == "Low":
        # Case 1: Preventive
        diet_items.append("Eat balanced meals with vegetables, fruits, whole grains")
        diet_items.append("Use less salt during cooking")
        diet_items.append("Drink water regularly unless advised otherwise")
        
    elif d_risk == "Medium" and k_risk == "Low":
        # Case 2: Early diabetes management
        diet_items.append("Reduce sugary drinks and desserts")
        diet_items.append("Choose whole grains over white rice or bread")
        diet_items.append("Limit salty processed foods")
        
    elif d_risk == "High" and k_risk == "Low":
        # Case 3: Strict diabetes control
        diet_items.append("Strict low-sugar diet")
        diet_items.append("Controlled portion sizes")
        diet_items.append("Avoid sweetened beverages completely")
        
    elif d_risk == "Low" and k_risk == "Medium":
        # Case 4: Kidney-friendly
        diet_items.append("Limit salt to reduce blood pressure strain")
        diet_items.append("Moderate protein intake (not excessive)")
        diet_items.append("Prefer fresh foods over canned foods")
        
    elif d_risk == "Low" and k_risk == "High":
        # Case 5: Dialysis-aware or Pre-dialysis
        if egfr and egfr < 15:
            diet_items.append("Reduce salt to prevent swelling")
            diet_items.append("Potassium and phosphorus intake based on lab values")
            diet_items.append("Protein intake must be individualized (do NOT self-restrict)")
        else:
            diet_items.append("Limit salt to reduce blood pressure strain")
            diet_items.append("Moderate protein intake (~0.8 g/kg)")
            diet_items.append("Limit phosphorus intake")
            
    elif d_risk == "High" and k_risk == "High":
        # Case 6: Combined critical
        diet_items.append("Maintain tight glycemic control")
        diet_items.append("Adhere to a renal-protective diet (low phosphorus/potassium)")
        diet_items.append("Restrict dietary sodium and potassium intake")
    
    # Additional mixed scenarios
    elif d_risk == "Medium" and k_risk == "Medium":
        # Both moderate - combined management
        diet_items.append("Low-glycemic foods (vegetables, legumes)")
        diet_items.append("Limit salt to < 2000 mg/day")
        diet_items.append("Moderate protein intake")
        
    elif d_risk == "Medium" and k_risk == "High":
        # Moderate diabetes + High kidney - renal priority
        if egfr and egfr < 15:
            diet_items.append("Strict sodium control")
            diet_items.append("Reduce sugary foods")
            diet_items.append("Potassium/phosphorus guided by labs")
        else:
            diet_items.append("Low-glycemic, renal-protective diet")
            diet_items.append("Limit salt and sugar")
            diet_items.append("Moderate protein (~0.8 g/kg)")
            
    elif d_risk == "High" and k_risk == "Medium":
        # High diabetes + Moderate kidney - balance both
        diet_items.append("Strict low-glycemic diet")
        diet_items.append("Limit sodium to < 2000 mg/day")
        diet_items.append("Moderate protein intake")
        
    else:
        # Catch-all fallback
        if d_risk == "High":
            diet_items.append("Low-glycemic diet (vegetables, legumes)")
        if k_risk in ["Medium", "High"]:
            diet_items.append("Limit sodium intake")
            
    # Add specific alerts
    if bmi >= 30:
        diet_items.append("⚠ Nutritional counseling recommended for weight management")
    if potassium > 5.0:
        diet_items.append("⚠ Limit high-potassium foods (bananas, potatoes, tomatoes)")
    
    diet_html = f"""
    <div class="mb-4">
        <h5 class="text-success mb-2 border-bottom pb-2"><i class="bi bi-egg-fried me-2"></i>Daily Diet Guidance</h5>
        <ul class="mb-0">
            {"".join([f'<li>{item}</li>' for item in diet_items])}
        </ul>
    </div>
    """
    sections.append(diet_html)
    
    # SECTION 4: PHYSICAL ACTIVITY
    activity_items = []
    
    if d_risk == "Low" and k_risk == "Low":
        activity_items.append("30 minutes of walking, cycling, or swimming most days")
        activity_items.append("Stay active but avoid extreme exertion")
    elif d_risk == "Medium" and k_risk == "Low":
        activity_items.append("Walk 10–15 minutes after meals")
        activity_items.append("Aim for weight reduction if overweight")
    elif d_risk == "High" and k_risk == "Low":
        activity_items.append("Low-impact exercise only")
        activity_items.append("Avoid skipping meals before activity")
    elif d_risk == "Low" and k_risk == "Medium":
        activity_items.append("Gentle daily activity (walking, stretching)")
        activity_items.append("Avoid dehydration")
    elif d_risk == "Low" and k_risk == "High":
        activity_items.append("Light walking and flexibility exercises")
        activity_items.append("Avoid strenuous activity")
    elif d_risk == "High" and k_risk == "High":
        activity_items.append("Only gentle movement as approved by doctor")
    
    # Additional mixed scenarios
    elif d_risk == "Medium" and k_risk == "Medium":
        activity_items.append("Moderate activity 20-30 mins/day")
        activity_items.append("Walking after meals recommended")
        activity_items.append("Avoid dehydration")
        
    elif d_risk == "Medium" and k_risk == "High":
        activity_items.append("Light walking and stretching only")
        activity_items.append("Avoid strenuous exercise")
        activity_items.append("Monitor for fatigue or swelling")
        
    elif d_risk == "High" and k_risk == "Medium":
        activity_items.append("Low-impact aerobic exercise")
        activity_items.append("20-30 minutes daily if tolerated")
        activity_items.append("Avoid prolonged fasting before activity")
        
    else:
        # Fallback for any remaining combinations
        activity_items.append("Light to moderate activity as tolerated")
        activity_items.append("Consult with healthcare provider for personalized plan")
    
    activity_html = f"""
    <div class="mb-4">
        <h5 class="text-primary mb-2 border-bottom pb-2"><i class="bi bi-activity me-2"></i>Physical Activity</h5>
        <ul class="mb-0">
            {"".join([f'<li>{item}</li>' for item in activity_items])}
        </ul>
    </div>
    """
    sections.append(activity_html)
    
    # SECTION 5: CLINICAL NOTES / WHEN TO SEEK CARE
    notes_items = []
    
    if d_risk == "Low" and k_risk == "Low":
        notes_items.append("Sudden swelling of legs or face")
        notes_items.append("Persistent fatigue or unexplained weight changes")
        notes_title = "When to Seek Care"
        notes_icon = "bi-info-circle"
        notes_color = "text-info"
    elif d_risk == "Medium" and k_risk == "Low":
        notes_items.append("Regular glucose monitoring recommended")
        notes_title = "Clinical Notes"
        notes_icon = "bi-clipboard-check"
        notes_color = "text-warning"
    elif d_risk == "High" and k_risk == "Low":
        notes_items.append("Proper diabetes control helps protect kidney function")
        notes_title = "Important Note"
        notes_icon = "bi-exclamation-triangle"
        notes_color = "text-danger"
    elif d_risk == "Low" and k_risk == "Medium":
        notes_items.append("Regular renal function monitoring")
        notes_items.append("Drink adequate fluids unless restricted")
        notes_title = "Clinical Notes"
        notes_icon = "bi-journal-medical"
        notes_color = "text-info"
    elif d_risk == "Low" and k_risk == "High":
        notes_items.append("Shortness of breath")
        notes_items.append("Rapid weight gain")
        notes_items.append("Reduced urine output")
        notes_title = "Warning Signs"
        notes_icon = "bi-exclamation-triangle-fill"
        notes_color = "text-danger"
    elif d_risk == "High" and k_risk == "High":
        notes_items.append("This condition requires coordinated care between kidney and diabetes specialists")
        notes_title = "Critical Notice"
        notes_icon = "bi-hospital-fill"
        notes_color = "text-danger"
    else:
        notes_items.append("Follow up with your healthcare provider")
        notes_title = "Clinical Notes"
        notes_icon = "bi-journal-medical"
        notes_color = "text-info"
    
    # Add Low BP note if applicable
    if bp_sys < 90:
        notes_items.append("Low blood pressure detected - ensure adequate hydration and clinical review")
    
    notes_html = f"""
    <div class="mb-4">
        <h5 class="{notes_color} mb-2 border-bottom pb-2"><i class="{notes_icon} me-2"></i>{notes_title}</h5>
        <ul class="mb-0">
            {"".join([f'<li>{item}</li>' for item in notes_items])}
        </ul>
    </div>
    """
    sections.append(notes_html)
    
    # SECTION 6: METRICS TABLE (Keep existing)
    REF_RANGES = {
        'Age': (None, None, 'years', 'Age'),
        'BMI': (18.5, 24.9, 'kg/m²', 'BMI'),
        'Glucose': (70, 100, 'mg/dL', 'Glucose (Fasting)'),
        'BP_Systolic': (90, 120, 'mmHg', 'Systolic BP'),
        'Creatinine': (0.6, 1.2, 'mg/dL', 'Creatinine'),
        'Pottasium': (3.5, 5.2, 'mEq/L', 'Potassium'),
        'Sodium': (135, 145, 'mEq/L', 'Sodium'),
        'Hemoglobin': (13.5, 17.5, 'g/dL', 'Hemoglobin'),
        'Urea': (7, 20, 'mg/dL', 'Blood Urea Nitrogen (BUN)'),
        'Albumin': (0, 0, 'Level', 'Urine Albumin (Dipstick)'),
        'eGFR': (90, None, 'mL/min/1.73m²', 'eGFR (Est.) \u003csmall class="text-muted"\u003e[Auto-calculated]\u003c/small\u003e')
    }

    metrics_rows = []
    
    def add_metric_row(key, val, label_override=None):
        if key not in REF_RANGES: return ""
        
        ref_min, ref_max, unit, name = REF_RANGES[key]
        if label_override: name = label_override
        
        status = '<span class="badge bg-success">Normal</span>'
        
        if key == 'eGFR':
            if val < 60: 
                status = '<span class="badge bg-danger">Low</span>'
            elif val < 90:
                status = '<span class="badge bg-warning text-dark">Mildly Reduced</span>'
        elif key == 'Albumin':
            if val > 0:
                status = '<span class="badge bg-danger">High/Trace</span>'
        else:
            if ref_max is not None and val > ref_max:
                status = '<span class="badge bg-danger">High</span>'
            elif ref_min is not None and val < ref_min:
                status = '<span class="badge bg-warning text-dark">Low</span>'
        
        range_str = "N/A"
        if ref_min is not None and ref_max is not None:
             range_str = f"{ref_min} - {ref_max}"
        elif ref_min is not None:
             range_str = f"> {ref_min}"
        elif ref_max is not None:
             range_str = f"< {ref_max}"
             
        return f"""
        <tr>
            <td><strong>{name}</strong></td>
            <td>{val} <small class="text-muted">{unit}</small></td>
            <td>{range_str}</td>
            <td>{status}</td>
        </tr>
        """

    metrics_rows.append(add_metric_row('Age', age))
    metrics_rows.append(add_metric_row('BMI', round(bmi, 1)))
    metrics_rows.append(add_metric_row('Glucose', round(glucose, 0)))
    metrics_rows.append(add_metric_row('BP_Systolic', round(bp_sys, 0)))
    metrics_rows.append(add_metric_row('Creatinine', round(creatinine, 2)))
    metrics_rows.append(add_metric_row('eGFR', egfr))
    
    p_val = features.get('Pottasium')
    if p_val: metrics_rows.append(add_metric_row('Pottasium', float(p_val)))
    
    s_val = features.get('Sodium')
    if s_val: metrics_rows.append(add_metric_row('Sodium', float(s_val)))
    
    h_val = features.get('Hemoglobin')
    if h_val: metrics_rows.append(add_metric_row('Hemoglobin', float(h_val)))
    
    u_val = features.get('Urea')
    if u_val: metrics_rows.append(add_metric_row('Urea', float(u_val)))
    
    a_val = features.get('Albumin')
    if a_val is not None: metrics_rows.append(add_metric_row('Albumin', int(float(a_val))))

    metrics_html = f"""
    <div class="mb-4">
        <h5 class="mb-3 border-bottom pb-2 text-secondary">Complete Patient Vitals & Labs</h5>
        <div class="table-responsive">
            <table class="table table-hover mb-0 align-middle" style="font-size: 0.9em;">
                <thead class="table-light">
                    <tr>
                        <th style="width: 30%">Metric</th>
                        <th style="width: 25%">Value</th>
                        <th style="width: 25%">Reference Range</th>
                        <th style="width: 20%">Status</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(metrics_rows)}
                </tbody>
            </table>
        </div>
    </div>
    """
    sections.append(metrics_html)
    
    # Combine all
    full_text = "\n".join(sections)
    
    # Generate simple interpretations for list view summaries
    d_summary = f"Risk: {d_risk}."
    k_summary = f"Risk: {k_risk}."
    
    return full_text, d_summary, k_summary
