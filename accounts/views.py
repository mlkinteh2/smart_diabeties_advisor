from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import PatientRegistrationForm
from .models import Patient, Doctor

def role_selection_view(request):
    """Display role selection page for Doctor/Patient/Admin"""
    if request.user.is_authenticated:
        return redirect_based_on_role(request.user)
    return render(request, 'accounts/role_selection.html')

def register_view(request):
    """Deprecated public registration view"""
    messages.warning(request, "Public registration is disabled. Please contact a doctor to register.")
    return redirect('login')

def doctor_register_patient_view(request):
    """View for doctors to register new patients"""
    # Ensure user is logged in and is a doctor
    if not request.user.is_authenticated:
        return redirect('login')
    
    if not hasattr(request.user, 'doctor'):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Access denied. Doctor privileges required.")

    if request.method == "POST":
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            
            # Create patient profile and verify immediately since doctor is registering
            Patient.objects.create(
                user=user,
                age=form.cleaned_data['age'],
                gender=form.cleaned_data['gender'],
                phone=form.cleaned_data['phone'],
                is_verified=True  # Auto-verify
            )
            
            messages.success(request, f"Patient {user.username} registered successfully!")
            return redirect('doctor_dashboard')
    else:
        form = PatientRegistrationForm()
    return render(request, "accounts/doctor_register_patient.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect_based_on_role(user)
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, "accounts/login.html", {"form": form})

def doctor_login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                # Check if user is actually a doctor
                if hasattr(user, 'doctor'):
                    login(request, user)
                    return redirect('doctor_dashboard')
                else:
                    messages.error(request, "Access denied. Not a doctor account.")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, "accounts/doctor_login.html", {"form": form})

def admin_login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                # Check if user is superuser
                if user.is_superuser:
                    login(request, user)
                    return redirect('admin_dashboard')
                else:
                    messages.error(request, "Access denied. Not an admin account.")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, "accounts/admin_login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("role_selection")

def redirect_based_on_role(user):
    if hasattr(user, 'doctor'):
        return redirect('doctor_dashboard')
    elif user.is_superuser:
        return redirect('admin_dashboard')
    else:
        # Check if patient is verified
        if hasattr(user, 'patient') and not user.patient.is_verified:
            return redirect('verification_pending')
        return redirect('patient_dashboard')

def verification_pending(request):
    """Display verification pending page for unverified patients"""
    return render(request, 'accounts/verification_pending.html')

def verify_patient(request, patient_id):
    """Doctor-only view to verify a patient"""
    from django.contrib.auth.decorators import login_required
    from django.http import HttpResponseForbidden
    from django.utils import timezone
    import logging
    
    # Ensure user is logged in and is a doctor
    if not request.user.is_authenticated:
        return redirect('login')
    
    if not hasattr(request.user, 'doctor'):
        return HttpResponseForbidden("Access denied. Doctor privileges required.")
    
    if request.method == "POST":
        try:
            patient = Patient.objects.get(id=patient_id)
            patient.is_verified = True
            patient.save()
            
            # Log verification action
            logger = logging.getLogger(__name__)
            logger.info(f"Patient {patient.user.username} (ID: {patient.id}) verified by Dr. {request.user.username} at {timezone.now()}")
            
            messages.success(request, f"Patient {patient.user.username} verified successfully!")
            return redirect('doctor_dashboard')
        except Patient.DoesNotExist:
            messages.error(request, "Patient not found.")
            return redirect('doctor_dashboard')
    
    return redirect('doctor_dashboard')
