from django.db import models
from predictions.models import Prediction

class Recommendation(models.Model):
    prediction = models.OneToOneField(Prediction, on_delete=models.CASCADE, related_name="recommendation")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Recommendation for Prediction #{self.prediction.id}"
