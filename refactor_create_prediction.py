
import os

content = """{% extends 'dashboard/doctor_base.html' %}
{% load static %}

{% block title %}Create Prediction - MedPredict AI{% endblock %}

{% block doctor_content %}
<style>
    /* Page specific styles */
    .page-header {
        margin-bottom: 2rem;
    }

    .page-header h1 {
        font-size: 1.5rem;
        font-weight: 700;
        color: #0f172a;
        margin: 0 0 0.25rem 0;
    }

    .page-header p {
        color: #64748b;
        font-size: 0.875rem;
        margin: 0;
    }

    /* Form Card */
    .form-card {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        max-width: 900px;
    }

    /* Tabs - Pill Style */
    .prediction-tabs {
        background: #f8fafc;
        padding: 0.375rem;
        border-radius: 8px;
        display: flex;
        gap: 0.5rem;
        margin-bottom: 2rem;
        border: 1px solid #e2e8f0;
    }

    .tab-button {
        flex: 1;
        background: transparent;
        border: none;
        border-radius: 6px;
        padding: 0.625rem 1rem;
        color: #64748b;
        font-weight: 600;
        font-size: 0.875rem;
        cursor: pointer;
        transition: all 0.2s;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }

    .tab-button:hover {
        color: #0f172a;
    }

    .tab-button.active {
        background: white;
        color: #2563eb;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    }

    /* Form Fields */
    .tab-content {
        display: none;
    }

    .tab-content.active {
        display: block;
    }

    .form-row {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.5rem;
        margin-bottom: 1.5rem;
    }

    .form-row.full {
        grid-template-columns: 1fr;
    }

    .form-group {
        margin: 0;
    }

    .form-group label {
        display: block;
        font-weight: 600;
        color: #334155;
        margin-bottom: 0.5rem;
        font-size: 0.875rem;
    }

    .input-wrapper {
        position: relative;
    }

    .input-icon {
        position: absolute;
        left: 1rem;
        top: 50%;
        transform: translateY(-50%);
        color: #94a3b8;
        font-size: 1rem;
    }

    .form-group input,
    .form-group select {
        width: 100%;
        padding: 0.75rem 1rem 0.75rem 2.75rem;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        font-size: 0.95rem;
        color: #0f172a;
        transition: all 0.2s;
        background: white;
    }

    .form-group input:focus,
    .form-group select:focus {
        outline: none;
        border-color: #2563eb;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    }

    .form-group input:disabled {
        background: #f1f5f9;
        cursor: not-allowed;
    }

    .form-group input::placeholder {
        color: #94a3b8;
    }

    /* Actions */
    .form-actions {
        display: flex;
        gap: 1rem;
        margin-top: 2.5rem;
        padding-top: 0;
    }

    .btn-primary {
        background: #2563eb;
        color: white;
        border: none;
        padding: 0.875rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.95rem;
        cursor: pointer;
        transition: all 0.2s;
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        text-decoration: none;
    }

    .btn-primary:hover {
        background: #1d4ed8;
        color: white;
    }

    .btn-secondary {
        background: #e2e8f0;
        color: #475569;
        border: none;
        padding: 0.875rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.95rem;
        cursor: pointer;
        transition: all 0.2s;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        display: flex;
        justify-content: center;
    }

    .btn-secondary:hover {
        background: #cbd5e1;
        color: #1e293b;
    }

    /* Error Alert */
    .alert-error {
        background-color: #fee2e2;
        border: 1px solid #fecaca;
        color: #991b1b;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
</style>

<div class="page-header">
    <h1>New Prediction</h1>
    <p>Generate AI-powered risk assessment for <strong>{{ patient.user.get_full_name|default:patient.user.username }}</strong></p>
</div>

{% if error %}
<div class="alert-error">
    <i class="bi bi-exclamation-circle-fill"></i>
    <span>{{ error }}</span>
</div>
{% endif %}

<div class="form-card">
    <form method="post" action="{% url 'create_prediction' patient.id %}">
        {% csrf_token %}

        <!-- Tabs -->
        <div class="prediction-tabs">
            <button type="button" class="tab-button active" onclick="switchTab('diabetes')">
                <i class="bi bi-heart-pulse"></i>
                Diabetes Risk Assessment
            </button>
            <button type="button" class="tab-button" onclick="switchTab('kidney')">
                <i class="bi bi-lungs"></i>
                Kidney Disease Assessment
            </button>
        </div>

        <!-- Diabetes Tab -->
        <div id="diabetes-tab" class="tab-content active">
            <div class="form-row full">
                <div class="form-group">
                    <label for="patient_name">Patient Name</label>
                    <div class="input-wrapper">
                        <i class="bi bi-person input-icon"></i>
                        <input type="text" id="patient_name"
                            value="{{ patient.user.get_full_name|default:patient.user.username }}" disabled>
                    </div>
                </div>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label for="age">Age (years)</label>
                    <div class="input-wrapper">
                        <i class="bi bi-calendar input-icon"></i>
                        <input type="number" id="age" name="age" placeholder="Enter age"
                            value="{{ patient.age }}" required>
                    </div>
                </div>
                <div class="form-group">
                    <label for="bmi">BMI (kg/m²)</label>
                    <div class="input-wrapper">
                        <i class="bi bi-rulers input-icon"></i>
                        <input type="number" step="0.1" id="bmi" name="bmi" placeholder="Enter BMI" required>
                    </div>
                </div>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label for="blood_pressure_diabetes">Blood Pressure (mmHg)</label>
                    <div class="input-wrapper">
                        <i class="bi bi-heart-pulse input-icon"></i>
                        <input type="text" id="blood_pressure_diabetes" name="blood_pressure"
                            placeholder="e.g., 120/80" required>
                    </div>
                </div>
                <div class="form-group">
                    <label for="glucose">Glucose Level (mg/dL)</label>
                    <div class="input-wrapper">
                        <i class="bi bi-droplet input-icon"></i>
                        <input type="number" step="0.1" id="glucose" name="glucose"
                            placeholder="Enter glucose level" required>
                    </div>
                </div>
            </div>
        </div>

        <!-- Kidney Tab -->
        <div id="kidney-tab" class="tab-content">
            <div class="form-row full">
                <div class="form-group">
                    <label for="patient_name_kidney">Patient Name</label>
                    <div class="input-wrapper">
                        <i class="bi bi-person input-icon"></i>
                        <input type="text" id="patient_name_kidney"
                            value="{{ patient.user.get_full_name|default:patient.user.username }}" disabled>
                    </div>
                </div>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label for="creatinine">Creatinine (mg/dL)</label>
                    <div class="input-wrapper">
                        <i class="bi bi-flask input-icon"></i>
                        <input type="number" step="0.01" id="creatinine" name="creatinine"
                            placeholder="Enter creatinine level">
                    </div>
                </div>
                <div class="form-group">
                    <label for="potassium">Potassium (mEq/L)</label>
                    <div class="input-wrapper">
                        <i class="bi bi-lightning-charge input-icon"></i>
                        <input type="number" step="0.1" id="potassium" name="potassium"
                            placeholder="Enter potassium level">
                    </div>
                </div>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label for="hemoglobin">Hemoglobin (g/dL)</label>
                    <div class="input-wrapper">
                        <i class="bi bi-droplet-half input-icon"></i>
                        <input type="number" step="0.1" id="hemoglobin" name="hemoglobin"
                            placeholder="Enter hemoglobin level">
                    </div>
                </div>
                <div class="form-group">
                    <label for="sodium">Sodium (mEq/L)</label>
                    <div class="input-wrapper">
                        <i class="bi bi-water input-icon"></i>
                        <input type="number" step="0.1" id="sodium" name="sodium"
                            placeholder="Enter sodium level">
                    </div>
                </div>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label for="blood_pressure_kidney">Blood Pressure (mmHg)</label>
                    <div class="input-wrapper">
                        <i class="bi bi-heart-pulse input-icon"></i>
                        <input type="text" id="blood_pressure_kidney" name="kidney_bp"
                            placeholder="e.g., 120/80">
                    </div>
                </div>
                <div class="form-group">
                    <label for="rbc">Red Blood Cells (RBC)</label>
                    <div class="input-wrapper">
                        <i class="bi bi-activity input-icon"></i>
                        <select id="rbc" name="rbc">
                            <option value="normal">Normal</option>
                            <option value="abnormal">Abnormal</option>
                        </select>
                    </div>
                </div>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label for="urea">Urea (mg/dL)</label>
                    <div class="input-wrapper">
                        <i class="bi bi-droplet input-icon"></i>
                        <input type="number" step="0.1" id="urea" name="urea" placeholder="Enter urea level">
                    </div>
                </div>
                <div class="form-group">
                    <label for="albumin">Albumin (Urinary: 0-5)</label>
                    <div class="input-wrapper">
                        <i class="bi bi-capsule input-icon"></i>
                        <select id="albumin" name="albumin">
                            <option value="0">0 - Normal</option>
                            <option value="1">1 - Trace</option>
                            <option value="2">2 - Mild</option>
                            <option value="3">3 - Moderate</option>
                            <option value="4">4 - High</option>
                            <option value="5">5 - Severe</option>
                        </select>
                    </div>
                </div>
            </div>
        </div>

        <!-- Actions -->
        <div class="form-actions">
            <button type="submit" class="btn-primary">
                <i class="bi bi-stars"></i>
                Generate Prediction
            </button>
            <a href="{% url 'doctor_dashboard' %}" class="btn-secondary">
                Cancel
            </a>
        </div>
    </form>
</div>
{% endblock %}

{% block extra_js %}
<script>
    function switchTab(tabName) {
        // Hide all tabs
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.classList.remove('active');
        });

        // Remove active class from all buttons
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('active');
        });

        // Show selected tab
        document.getElementById(tabName + '-tab').classList.add('active');

        // Add active class to clicked button
        event.target.closest('.tab-button').classList.add('active');
    }
</script>
{% endblock %}
"""

path = r"d:\Projects\Final_Project\medpredict\predictions\templates\predictions\create_prediction.html"
with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Successfully overwrote file:", path)
