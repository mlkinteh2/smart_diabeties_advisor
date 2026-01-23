from django.shortcuts import render, get_object_or_404
from .models import Recommendation

def recommendation_detail(request, prediction_id):
    recommendation = get_object_or_404(Recommendation, prediction_id=prediction_id)
    return render(request, "recommendations/recommendation_detail.html", {
        "recommendation": recommendation
    })

def recommendation_list(request):
    recommendations = Recommendation.objects.all()
    return render(request, "recommendations/recommendation_list.html", {
        "recommendations": recommendations
    })
