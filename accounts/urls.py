from django.urls import path
from . import views

urlpatterns = [
    path('', views.role_selection_view, name='root_redirect'),
    path('role-selection/', views.role_selection_view, name='role_selection'),
    path('doctor/login/', views.doctor_login_view, name='doctor_login'),
    path('admin/login/', views.admin_login_view, name='admin_login'),
    path('login/', views.login_view, name='login'),
    path('doctor/register-patient/', views.doctor_register_patient_view, name='doctor_register_patient'),
    # path('register/', views.register_view, name='register'), # Public registration disabled
    path('logout/', views.logout_view, name='logout'),
    path('verification-pending/', views.verification_pending, name='verification_pending'),
    path('doctor/verify-patient/<int:patient_id>/', views.verify_patient, name='verify_patient'),
]
