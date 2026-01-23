from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from accounts.models import Patient, Doctor
from predictions.models import Prediction

@login_required
def admin_dashboard(request):
    """Admin dashboard with system statistics and monitoring"""
    # Ensure user is superuser
    if not request.user.is_superuser:
        return redirect('doctor_dashboard' if hasattr(request.user, 'doctor') else 'patient_dashboard')
    
    # Statistics
    total_users = User.objects.count()
    active_doctors = Doctor.objects.count()
    active_patients = Patient.objects.filter(is_verified=True).count()
    total_predictions = Prediction.objects.count()
    
    # Prediction Statistics
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = now - timedelta(days=7)
    month_start = now - timedelta(days=30)
    
    todays_predictions = Prediction.objects.filter(created_at__gte=today_start).count()
    week_predictions = Prediction.objects.filter(created_at__gte=week_start).count()
    month_predictions = Prediction.objects.filter(created_at__gte=month_start).count()
    
    approved_predictions = Prediction.objects.filter(approval_status='Approved').count()
    approval_rate = (approved_predictions / total_predictions * 100) if total_predictions > 0 else 0
    
    # Recent Activity (last 10 activities)
    recent_activities = []
    
    # Recent doctors
    recent_doctors = Doctor.objects.select_related('user').order_by('-id')[:3]
    for doctor in recent_doctors:
        recent_activities.append({
            'type': 'doctor_registered',
            'icon': 'bi-person-plus',
            'color': 'primary',
            'title': 'New doctor registered',
            'description': f'Dr. {doctor.user.get_full_name() or doctor.user.username}',
            'timestamp': doctor.user.date_joined
        })
    
    # Recent approved predictions
    recent_approvals = Prediction.objects.filter(approval_status='Approved').select_related('patient__user', 'doctor__user').order_by('-created_at')[:3]
    for pred in recent_approvals:
        recent_activities.append({
            'type': 'prediction_approved',
            'icon': 'bi-check-circle',
            'color': 'success',
            'title': 'Prediction approved',
            'description': f'Dr. {pred.doctor.user.username if pred.doctor else "Unknown"}',
            'timestamp': pred.created_at
        })
    
    # Recent patients
    recent_patients = Patient.objects.select_related('user').order_by('-id')[:2]
    for patient in recent_patients:
        recent_activities.append({
            'type': 'patient_created',
            'icon': 'bi-person-check',
            'color': 'info',
            'title': 'Patient account created',
            'description': patient.user.get_full_name() or patient.user.username,
            'timestamp': patient.user.date_joined
        })
    
    # High-risk predictions
    high_risk_predictions = Prediction.objects.filter(
        Q(diabetes_risk='High') | Q(kidney_risk='High')
    ).select_related('patient__user', 'doctor__user').order_by('-created_at')[:2]
    
    for pred in high_risk_predictions:
        recent_activities.append({
            'type': 'high_risk',
            'icon': 'bi-exclamation-triangle',
            'color': 'danger',
            'title': 'High-risk prediction flagged',
            'description': f'Dr. {pred.doctor.user.username if pred.doctor else "Pending"}',
            'timestamp': pred.created_at
        })
    
    # Sort activities by timestamp
    recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)
    recent_activities = recent_activities[:10]
    
    # System Health Metrics (simulated for now)
    import random
    system_health = {
        'api_response_time': random.randint(80, 150),
        'database_load': random.randint(25, 45),
        'server_uptime': round(random.uniform(99.5, 99.9), 1),
        'active_sessions': random.randint(70, 100)
    }
    
    context = {
        'total_users': total_users,
        'active_doctors': active_doctors,
        'active_patients': active_patients,
        'total_predictions': total_predictions,
        'todays_predictions': todays_predictions,
        'week_predictions': week_predictions,
        'month_predictions': month_predictions,
        'approval_rate': round(approval_rate, 1),
        'recent_activities': recent_activities,
        'system_health': system_health,
    }
    
    return render(request, 'dashboard/admin_dashboard.html', context)

@login_required
def user_management(request):
    """Custom user management view matching the requested design"""
    if not request.user.is_superuser:
        return redirect('doctor_dashboard' if hasattr(request.user, 'doctor') else 'patient_dashboard')
    
    # Query parameters for filtering
    role_filter = request.GET.get('role', 'all')
    search_query = request.GET.get('search', '')
    
    users_data = []
    
    # Get all users (excluding superusers if you want, or include them)
    users = User.objects.all().order_by('-date_joined')
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) | 
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    for user in users:
        u_data = {
            'id': user.id,
            'name': user.get_full_name() or user.username,
            'email': user.email,
            'initials': (user.first_name[0] if user.first_name else '') + (user.last_name[0] if user.last_name else user.username[0].upper()),
            'status': 'Active' if user.is_active else 'Inactive',
            'joined': user.date_joined,
            'role': 'Admin' if user.is_superuser else None,
        }
        
        # Doctor check
        if hasattr(user, 'doctor'):
            u_data['role'] = 'Doctor'
            u_data['doctor_id'] = user.doctor.id
            u_data['activity_main'] = f"{user.doctor.reviewed_predictions.count()} predictions"
            u_data['activity_sub'] = f"Specialization: {user.doctor.specialization}"
        
        # Patient check
        elif hasattr(user, 'patient'):
            u_data['role'] = 'Patient'
            u_data['patient_id'] = user.patient.id
            u_data['activity_main'] = f"{user.patient.predictions.count()} assessments"
            last_pred = user.patient.predictions.first()
            u_data['activity_sub'] = f"Last: {last_pred.created_at.strftime('%Y-%m-%d')}" if last_pred else "No activity yet"
            
        # Filter logic
        if role_filter == 'doctors' and u_data['role'] != 'Doctor':
            continue
        if role_filter == 'patients' and u_data['role'] != 'Patient':
            continue
            
        if u_data['role']: # Only include if they have a role (and not just raw User)
            users_data.append(u_data)
            
    context = {
        'users_data': users_data,
        'role_filter': role_filter,
        'search_query': search_query,
    }
    
    return render(request, 'dashboard/user_management.html', context)

@login_required
def delete_user(request, user_id):
    """Custom user deletion with confirmation using dashboard layout"""
    if not request.user.is_superuser:
        return redirect('admin_dashboard')
    
    user_to_delete = get_object_or_404(User, id=user_id)
    
    # Prevent self-deletion
    if user_to_delete == request.user:
        return redirect('user_management')
        
    if request.method == 'POST':
        user_to_delete.delete()
        return redirect('user_management')
        
    context = {
        'user_to_delete': user_to_delete,
    }
    return render(request, 'dashboard/delete_user_confirm.html', context)
