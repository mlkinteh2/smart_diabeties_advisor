from django.contrib import admin
from .models import Prediction, PredictionFeature

admin.site.register(Prediction)
admin.site.register(PredictionFeature)
