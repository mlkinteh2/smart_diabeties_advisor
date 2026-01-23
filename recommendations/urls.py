from django.urls import path
from . import views

urlpatterns = [
    path("<int:prediction_id>/", views.recommendation_detail, name="recommendation_detail"),
]
