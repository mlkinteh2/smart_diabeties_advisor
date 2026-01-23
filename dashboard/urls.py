from django.urls import path
from . import views, admin_views

urlpatterns = [
    # Home redirect
    path("dashboard/", views.home, name="dashboard"),
    
    # Doctor Routes
    path("doctor/dashboard/", views.doctor_dashboard, name="doctor_dashboard"),
    path("doctor/prediction/<int:id>/", views.doctor_prediction_detail, name="doctor_prediction_detail"),
    path("doctor/approve/<int:id>/", views.approve_prediction, name="approve_prediction"),
    path("doctor/reject/<int:id>/", views.reject_prediction, name="reject_prediction"),
    
    # Patient Routes
    path("patient/dashboard/", views.patient_dashboard, name="patient_dashboard"),
    path("patient/prediction/<int:id>/", views.patient_prediction_detail, name="patient_prediction_detail"),
    path("patient/history/", views.patient_history, name="patient_history"),
    path("patient/recommendations/", views.patient_recommendations, name="patient_recommendations"),
    path("patient/latest-report/", views.patient_latest_report, name="patient_latest_report"),
    # Admin Routes
    path("admin/dashboard/", admin_views.admin_dashboard, name="admin_dashboard"),
    path("admin/users/", admin_views.user_management, name="user_management"),
    path("admin/users/delete/<int:user_id>/", admin_views.delete_user, name="delete_user"),
]
