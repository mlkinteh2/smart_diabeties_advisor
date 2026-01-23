from django.db import models
from accounts.models import Patient, Doctor

class Prediction(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="predictions")
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_predictions")

    # Diabetes results
    diabetes_probability = models.FloatField(null=True, blank=True)
    diabetes_label = models.IntegerField(null=True, blank=True)
    diabetes_risk = models.CharField(max_length=20, null=True, blank=True)

    # Kidney results
    kidney_probability = models.FloatField(null=True, blank=True)
    kidney_label = models.IntegerField(null=True, blank=True)
    kidney_risk = models.CharField(max_length=20, null=True, blank=True)

    # Approval workflow
    approval_status = models.CharField(
        max_length=20,
        choices=[
            ("Pending", "Pending"),
            ("Approved", "Approved"),
            ("Rejected", "Rejected"),
        ],
        default="Pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    # Explainability - Diabetes
    diabetes_shap_image = models.CharField(max_length=500, null=True, blank=True)
    diabetes_fi_image = models.CharField(max_length=500, null=True, blank=True)
    
    # Explainability - Kidney
    kidney_shap_image = models.CharField(max_length=500, null=True, blank=True)
    kidney_fi_image = models.CharField(max_length=500, null=True, blank=True)
    
    # Recommendations
    recommendation_text = models.TextField(null=True, blank=True)
    doctor_notes = models.TextField(null=True, blank=True)

    # Clinical Explanations (Plain English)
    diabetes_explanation = models.TextField(null=True, blank=True)
    kidney_explanation = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Prediction #{self.id} for {self.patient.user.username}"
    

class PredictionFeature(models.Model):
    prediction = models.ForeignKey(Prediction, on_delete=models.CASCADE, related_name="features")
    feature_name = models.CharField(max_length=100)
    feature_value = models.CharField(max_length=100)
    shap_value = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["feature_name"]

    def __str__(self):
        return f"{self.feature_name}: {self.feature_value}"


