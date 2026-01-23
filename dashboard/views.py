from django.shortcuts import render, redirect, get_object_or_404
from predictions.models import Prediction, PredictionFeature
from recommendations.models import Recommendation
from accounts.models import Doctor
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from accounts.decorators import verified_patient_required

def home(request):
    if not request.user.is_authenticated:
        return redirect("login")
    if hasattr(request.user, "doctor"):
        return redirect("doctor_dashboard")
    elif hasattr(request.user, "patient"):
        return redirect("patient_dashboard")
    elif request.user.is_superuser:
        return redirect("admin_dashboard")
    else:
        return redirect("login") # Fallback


@login_required
def doctor_dashboard(request):
    # Ensure logged in user is a doctor
    if not hasattr(request.user, "doctor"):
        return render(request, "dashboard/not_doctor.html")

    predictions = Prediction.objects.filter(approval_status="Pending").order_by("-created_at")
    
    # Stats
    total_predictions = Prediction.objects.filter(doctor=request.user.doctor).count()
    todays_predictions = Prediction.objects.filter(
        doctor=request.user.doctor, 
        created_at__date=timezone.now().date()
    ).count()
    patients_monitored = Prediction.objects.filter(doctor=request.user.doctor).values('patient').distinct().count()
    
    # Get all patients for the patient list
    from accounts.models import Patient
    patients = Patient.objects.all().order_by('user__username')
    
    # Get unverified patients
    unverified_patients = Patient.objects.filter(is_verified=False).order_by('user__username')

    return render(request, "dashboard/doctor_dashboard.html", {
        "predictions": predictions,
        "patients": patients,
        "unverified_patients": unverified_patients,
        "total_predictions": total_predictions,
        "todays_predictions": todays_predictions,
        "patients_monitored": patients_monitored,
        "pending_count": predictions.count(),
        "pending_approvals_count": predictions.count(),
        "pending_predictions": predictions[:5],  # Show first 5 in table
    })



@login_required
def doctor_prediction_detail(request, id):
    if not hasattr(request.user, "doctor"):
        return render(request, "dashboard/not_doctor.html")

    prediction = get_object_or_404(Prediction, id=id)
    features = PredictionFeature.objects.filter(prediction=prediction)

    return render(request, "dashboard/doctor_prediction_detail.html", {
        "prediction": prediction,
        "features": features
    })


@login_required
def approve_prediction(request, id):
    if not hasattr(request.user, "doctor"):
        return render(request, "dashboard/not_doctor.html")

    prediction = get_object_or_404(Prediction, id=id)

    if request.method == "POST":
        text = request.POST.get("text")

        Recommendation.objects.create(
            prediction=prediction,
            text=text
        )

        prediction.approval_status = "Approved"
        prediction.doctor = request.user.doctor
        prediction.save()

        return redirect("doctor_dashboard")

    return render(request, "dashboard/approve_prediction.html", {
        "prediction": prediction
    })


@login_required
def reject_prediction(request, id):
    if not hasattr(request.user, "doctor"):
        return render(request, "dashboard/not_doctor.html")

    prediction = get_object_or_404(Prediction, id=id)

    prediction.approval_status = "Rejected"
    prediction.doctor = request.user.doctor
    prediction.save()

    return redirect("doctor_dashboard")


from django.contrib.auth.decorators import login_required
from predictions.models import Prediction, PredictionFeature
from recommendations.models import Recommendation

@login_required
@verified_patient_required
def patient_dashboard(request):
    if not hasattr(request.user, "patient"):
        return render(request, "dashboard/not_patient.html")

    predictions = Prediction.objects.filter(patient=request.user.patient, approval_status="Approved").order_by("-created_at")
    
    # Statistics
    total_predictions = predictions.count()
    approved_predictions = predictions.filter(approval_status="Approved")
    
    # Get last risk levels
    last_diabetes_risk = "N/A"
    last_kidney_risk = "N/A"
    if approved_predictions.exists():
        latest = approved_predictions.first()
        last_diabetes_risk = latest.diabetes_risk or "N/A"
        last_kidney_risk = latest.kidney_risk or "N/A"
    
    # Risk history for chart (count by risk level)
    diabetes_low = approved_predictions.filter(diabetes_risk="Low").count()
    diabetes_medium = approved_predictions.filter(diabetes_risk="Medium").count()
    diabetes_high = approved_predictions.filter(diabetes_risk="High").count()
    
    kidney_low = approved_predictions.filter(kidney_risk="Low").count()
    kidney_medium = approved_predictions.filter(kidney_risk="Medium").count()
    kidney_high = approved_predictions.filter(kidney_risk="High").count()

    return render(request, "dashboard/patient_dashboard.html", {
        "latest_prediction": latest if approved_predictions.exists() else None,
        "predictions": predictions,
        "total_predictions": total_predictions,
        "approved_count": approved_predictions.count(),
        "pending_count": predictions.filter(approval_status="Pending").count(),
        "last_diabetes_risk": last_diabetes_risk,
        "last_kidney_risk": last_kidney_risk,
        "diabetes_low": diabetes_low,
        "diabetes_medium": diabetes_medium,
        "diabetes_high": diabetes_high,
        "kidney_low": kidney_low,
        "kidney_medium": kidney_medium,
        "kidney_high": kidney_high,
    })



@login_required
@verified_patient_required
def patient_prediction_detail(request, id):
    if not hasattr(request.user, "patient"):
        return render(request, "dashboard/not_patient.html")

    prediction = get_object_or_404(Prediction, id=id, patient=request.user.patient)
    features = PredictionFeature.objects.filter(prediction=prediction)
    recommendation = Recommendation.objects.filter(prediction=prediction).first()

    # Only show full data if approved
    if prediction.approval_status != "Approved":
        return render(request, "dashboard/waiting_approval.html", {
            "prediction": prediction
        })

    return render(request, "dashboard/patient_prediction_detail.html", {
        "prediction": prediction,
        "features": features,
        "recommendation": recommendation
    })



@login_required
@verified_patient_required
def patient_history(request):
    if not hasattr(request.user, "patient"):
        return render(request, "dashboard/not_patient.html")

    # Get all predictions for the table
    predictions = Prediction.objects.filter(patient=request.user.patient).order_by("-created_at")
    
    # Get approved predictions for the charts (limit to last 6 for clean display)
    approved_predictions = predictions.filter(approval_status="Approved").order_by("-created_at")[:6]
    
    # Prepare data for charts (reversed to show oldest to newest left-to-right)
    chart_data = list(reversed(approved_predictions))
    
    dates = [p.created_at.strftime("%m-%d") for p in chart_data]
    
    chart_diabetes = []
    for p in chart_data:
        prob = int(p.diabetes_probability or 0)
        risk_class = "low"
        if p.diabetes_risk == "High":
            risk_class = "high"
        elif p.diabetes_risk == "Medium":
            risk_class = "medium"
        chart_diabetes.append({'value': prob, 'class': risk_class})
        
    chart_kidney = []
    for p in chart_data:
        prob = int(p.kidney_probability or 0)
        risk_class = "low"
        if p.kidney_risk == "High":
            risk_class = "high"
        elif p.kidney_risk == "Medium":
            risk_class = "medium"
        chart_kidney.append({'value': prob, 'class': risk_class})

    return render(request, "dashboard/patient_history.html", {
        "predictions": predictions,  # Full list for table
        "chart_dates": dates,
        "chart_diabetes": chart_diabetes,
        "chart_kidney": chart_kidney,
    })


@login_required
@verified_patient_required
def patient_recommendations(request):
    if not hasattr(request.user, "patient"):
        return render(request, "dashboard/not_patient.html")

    predictions = Prediction.objects.filter(patient=request.user.patient, approval_status="Approved").order_by("-created_at")
    latest = predictions.first() if predictions.exists() else None

    return render(request, "dashboard/patient_recommendations.html", {
        "latest_prediction": latest
    })


@login_required
def patient_latest_report(request):
    if not hasattr(request.user, "patient"):
        return render(request, "dashboard/not_patient.html")

    predictions = Prediction.objects.filter(patient=request.user.patient, approval_status="Approved").order_by("-created_at")
    
    if predictions.exists():
        return redirect("patient_prediction_detail", id=predictions.first().id)
    
    # If no report exists, stay on dashboard or show a message
    return redirect("patient_dashboard")
