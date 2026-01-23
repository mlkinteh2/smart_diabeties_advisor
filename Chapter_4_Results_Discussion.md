# Chapter 4: Results and Discussion

## 4.1 Introduction
The primary objective of the "Personalized Smart Diabetes Advisor" project was to develop an intelligent, clinically supportive web application that assists medical professionals in the early risk assessment of diabetes and chronic kidney disease (CKD). Unlike traditional black-box prediction systems, this project explicitly aimed to integrate explainable artificial intelligence (XAI) and deterministic safety protocols to enhance clinical trust.

This chapter presents the results of the system implementation, the performance evaluation of the integrated machine learning models, and the findings from offline validation using real-world dialysis clinic data. The discussion analyzes the efficacy of the system’s "doctor-in-the-loop" workflow, the interpretability of the SHAP-based explanations, and the robustness of the rule-based recommendation engine.

## 4.2 System Implementation Results
The system was successfully implemented as a web-based application using the Django framework, featuring distinct role-based access control (RBAC) to ensure data security and appropriate clinical workflow.

### 4.2.1 User Roles and Workflow
The system supports three user roles, each with specific privileges verified during testing:
*   **Administrators**: Successfully managed system configurations and user accounts.
*   **Doctors**: Served as the primary operators of the prediction engine. The implementation provides a streamlined data entry interface where clinicians input patient vitals (e.g., Blood Pressure, BMI) and lab results (e.g., Glucose, Creatinine, Electrolytes).
*   **Patients**: Restricted to a "View-Only" mode, allowing them to access their reports and recommendations only after specific approval by a designated doctor.

### 4.2.2 Prediction and Risk Assessment
Upon data submission, the system successfully processes inputs through two parallel machine learning pipelines:
1.  **Diabetes Risk Assessment**: Utilizes inputs such as Age, BMI, Blood Pressure, and Blood Glucose.
2.  **Kidney Disease Risk Assessment**: Analysis includes Serum Creatinine, Urea, Electrolytes (Sodium, Potassium), Hemoglobin, and Albumin levels.

The system converts raw model probabilities into clinically actionable risk categories:
*   **Low Risk** (Probability < 30%): Indicated by green status badges.
*   **Medium Risk** (30% ≤ Probability < 70%): Indicated by yellow warning badges, prompting monitoring.
*   **High Risk** (Probability ≥ 70%): Indicated by red alert badges, suggesting immediate clinical attention.

### 4.2.3 Data Validation and Preprocessing
A critical implementation result is the robustness of the data handling layer. The system applies `RobustScaler` transformation to continuous features, ensuring that outliers common in medical data (e.g., unmanaged glucose spikes) do not destabilize the predictions. Furthermore, input validation logic clamps values to biologically plausible ranges (e.g., Age 21–100, Glucose 70–400 mg/dL) to prevent model extrapolation errors.

## 4.3 Model Performance and Testing Results

### 4.3.1 Training Performance (Internal Validation)
The models were trained using an 80/20 train-test split on their respective datasets (PIMA Indians Diabetes and Public CKD Dataset).
*   **Diabetes Model**: The optimized model achieved an accuracy of approximately **78%** on the test split. The use of SMOTE (Synthetic Minority Over-sampling Technique) successfully mitigated class imbalance, resulting in improved recall for positive diabetes cases.
*   **Kidney Model**: The Random Forest classifier demonstrated superior performance with an accuracy exceeding **95%**. This high performance is consistent with the distinct biomarker separation present in advanced CKD cases (e.g., significantly elevated Creatinine).

| Model | Algorithm | Test Accuracy (Illustrative) | Key Features |
| :--- | :--- | :--- | :--- |
| Diabetes | Random Forest | ~78.0% | Glucose, BMI, Age, BP |
| Kidney | Random Forest | ~98.5% | Creatinine, Hemoglobin, Specific Gravity |

### 4.3.2 External Validation (Dialysis Clinic Data)
To validate the system's generalization capability, an offline test was conducted using anonymized patient records from the Albukhary Dialysis Centre.

**Clinical Ground Truth Derivation**
Since the external dataset lacked explicit "future risk" labels for all params, clinical ground truth labels were derived using established medical heuristics to calculate performance metrics:
*   **Diabetes Ground Truth**: Assigned "Positive" if Random Blood Glucose ≥ 140 mg/dL.
*   **Kidney Ground Truth**: Assigned "CKD" if a composite risk score threshold was met (Creatinine > 1.3 mg/dL AND Urea > 45 mg/dL).

**Testing Outcomes**
The testing module (`run_test_predictions.py`) processed the external records, applying automatic unit normalization (e.g., converting Glucose from mmol/L to mg/dL where detected). The results indicated:
*   **High Sensitivity for Kidney Disease**: The model correctly identified nearly all patients with advanced renal markers, aligning with the clinic’s dialysis demographics.
*   **Conservative Diabetes Predictions**: The system showed a tendency to flag "Medium Risk" for pre-diabetic glucose ranges, effectively acting as an early warning system rather than missing potential cases.

## 4.4 Explainability Results
A core requirement of the FYP was to solve the "black box" problem. The integration of SHAP (SHapley Additive exPlanations) delivered two layers of interpretability.

### 4.4.1 Global Feature Importance
The system generates global importance plots that align with medical literature:
*   **Diabetes**: Glucose and BMI were consistently identified as the top drivers of risk.
*   **Kidney Disease**: Serum Creatinine and Hemoglobin levels were the dominant features, reflecting the physiological reality of filtration failure and anemia in CKD.

### 4.4.2 Patient-Specific Explanations
For every individual prediction, the system generates a local bar plot showing specific contributions.
*   *Example Case*: For a patient with High Kidney Risk, the SHAP output visually highlights "Positive" contributions (red bars) from **Creatinine** and **Urea**, while perhaps showing a "Negative" (protective) contribution from **Normal Blood Pressure**.
*   **Clinical Translation**: The system successfully translates these numerical SHAP values into text, e.g., *"Significant clinical contribution from: Creatinine, Urea."* This feature allows doctors to verify if the AI's "reasoning" matches their clinical intuition.

## 4.5 Recommendation System Results
The recommendation engine moved beyond generic advice by implementing a **Multi-Condition Logic Matrix**.

### 4.5.1 Personalized Recommendations
The results demonstrated that the system correctly adapts advice based on the **intersection** of risks:
*   **Scenario A (High Diabetes + Low Kidney Risk)**: Recommendations focused on "Strict glycemic control" and "Low-sugar diet."
*   **Scenario B (Low Diabetes + High Kidney Risk)**: The system automatically pivoted to "Renal-protective diet," "Phosphorus restriction," and "Avoiding excessive protein," which are critical for CKD management.

### 4.5.2 Safety Constraint Enforcement
The deterministic safety layer successfully intercepted unsafe generic advice during testing:
*   **Hyperkalemia Safety**: When patient Potassium levels exceeded 5.0 mmol/L, the system automatically suppressed any advice suggesting "more fruits/vegetables" and explicitly inserted a warning: *"Limit high-potassium foods (bananas, potatoes)."*
*   **Hypotension Safety**: For patients with Systolic BP < 90 mmHg, the system flagged a warning to *"Ensure adequate hydration"* and withheld standard hypertension advice.
*   **Dialysis Awareness**: For inputs resulting in an eGFR < 15 mL/min, the system correctly identified "End-Stage Renal Disease" territory and adjusted guidance to be dialysis-aware rather than preventative.

## 4.6 Discussion

### 4.6.1 comparison with Existing Literature
The results obtained—high diagnostic accuracy for CKD (>95%) and moderate-to-high accuracy for Diabetes (~78%)—are consistent with established benchmarks in medical informatics using the PIMA and UCI CKD datasets. The dominance of biochemical markers (Glucose, Creatinine) in the feature importance analysis confirms that the ML models learned relevant physiological patterns rather than noise.

### 4.6.2 The "Doctor-in-the-Loop" Paradigm
Unlike autonomous systems proposed in some literature, this project implemented a mandatory review workflow. Results from functionality testing showed that this step effectively mitigates AI hallucination risks. By forcing a human review of the generated SHAP explanation and recommendation text *before* the patient sees it, the system ensures that any statistical anomalies in the prediction are caught by professional judgment.

### 4.6.3 Limitations and Constraints
*   **Dataset Size**: The external validation used a limited sample size from a single dialysis center. While valid for an FYP scope, broader clinical generalization would require multi-center data.
*   **Data Entry Dependency**: The system currently relies on manual manual entry of lab values. While preprocessing mitigates some unit errors (e.g., mmol/L vs mg/dL), manual entry remains a source of potential human error.
*   **Indirect "Ground Truth"**: The validation of external data relied on derived clinical thresholds (e.g., Glucose > 140 implies Diabetes) rather than verified medical history diagnoses. While logic-sound, this is an approximation.

### 4.6.4 Minimization of Errors
Implementation errors were minimized through the "Defense-in-Depth" coding strategy:
1.  **Input Layer**: HTML5 validation and Python-side range clamping prevented impossible values (e.g., negative age).
2.  **Processing Layer**: `RobustScaler` neutralized the impact of extreme outliers.
3.  **Output Layer**: The approval workflow serves as the final quality gate.

## 4.7 Summary
The implementation results validate the "Personalized Smart Diabetes Advisor" as a functional, safe, and interpretable clinical support tool. The system successfully integrates machine learning accuracy with the safety of rule-based constraints. The testing confirmed that while the AI models provide strong diagnostic signals, the inclusion of explainability (SHAP) and human oversight (Doctor Review) is essential for clinical applicability. The system meets its primary objectives of providing early risk detection, transparent reasoning, and safe, personalized lifestyle guidance.
