from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def verified_patient_required(view_func):
    """
    Decorator to ensure patient is verified before accessing medical data.
    
    - If user is a doctor: allow access
    - If user is a verified patient: allow access
    - If user is an unverified patient: redirect to verification_pending page
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Allow doctors full access
        if hasattr(request.user, 'doctor'):
            return view_func(request, *args, **kwargs)
        
        # Check if user is a patient
        if hasattr(request.user, 'patient'):
            patient = request.user.patient
            
            # If patient is not verified, redirect to verification pending page
            if not patient.is_verified:
                messages.warning(request, "Your account is awaiting verification by a doctor.")
                return redirect('verification_pending')
        
        # Allow access if verified or not a patient
        return view_func(request, *args, **kwargs)
    
    return wrapper
