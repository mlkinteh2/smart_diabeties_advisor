from django import forms

class PredictionForm(forms.Form):
    # Diabetes inputs
    age = forms.FloatField()
    bmi = forms.FloatField()
    blood_pressure = forms.FloatField()
    glucose = forms.FloatField()

    # Kidney inputs
    creatinine = forms.FloatField()
    potassium = forms.FloatField()
    hemoglobin = forms.FloatField()
    sodium = forms.FloatField()
    urea = forms.FloatField()
    kidney_bp = forms.FloatField()
    rbc = forms.FloatField()
    albumin = forms.FloatField()
