from django.urls import path
from . import views

urlpatterns = [
    path("create/<int:patient_id>/", views.create_prediction, name="create_prediction"),
    path("list/", views.prediction_list, name="prediction_list"),
    path("<int:id>/", views.prediction_detail, name="prediction_detail"),
    path("<int:id>/review/", views.review_prediction, name="review_prediction"),
]
