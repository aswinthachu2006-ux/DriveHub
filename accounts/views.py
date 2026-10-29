from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile
from bookings.models import Booking
from datetime import datetime, date, timedelta

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        date_of_birth_str = request.POST.get('date_of_birth', '')
        phone = request.POST.get('phone', '').strip()
        cleaned_phone = phone.replace(' ', '').replace('-', '').replace('+91', '')
        if cleaned_phone.isdigit() and len(cleaned_phone) == 10:
            phone = f"+91 {cleaned_phone}"
        elif not phone.startswith('+91'):
            phone = f"+91 {phone}" if phone else "+91 98765 43210"
        address = request.POST.get('address', '').strip()

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return render(request, 'register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose a different one.")
            return render(request, 'register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "An account with this email address already exists.")
            return render(request, 'register.html')

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        # Update profile
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.phone = phone
        profile.address = address
        if date_of_birth_str:
            try:
                profile.date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        profile.save()

        # Log user in
        login(request, user)
        messages.success(request, f"Welcome to DriveHub, {first_name or username}! Your account is active.")
        return redirect('dashboard')

    return render(request, 'register.html')

signup_view = register_view

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')

@login_required
def dashboard_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    user_bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    
    total_bookings_count = user_bookings.count()
    active_bookings_count = user_bookings.filter(status__in=['Pending', 'Confirmed', 'Ongoing']).count()
    current_booking = user_bookings.filter(status__in=['Confirmed', 'Ongoing', 'Pending']).first()
    recent_bookings = user_bookings[:5]

    return render(request, 'dashboard.html', {
        'profile': profile,
        'total_bookings_count': total_bookings_count,
        'active_bookings_count': active_bookings_count,
        'current_booking': current_booking,
        'recent_bookings': recent_bookings,
    })

@login_required
def licence_upload_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        licence_number = request.POST.get('licence_number', '').strip().upper()
        issue_date_str = request.POST.get('licence_issue_date')
        expiry_date_str = request.POST.get('licence_expiry_date')
        licence_file = request.FILES.get('licence_image')

        # Clean licence number
        cleaned_dl = licence_number.replace(' ', '').replace('-', '')

        if not cleaned_dl or len(cleaned_dl) < 4:
            messages.error(request, "Please enter a valid licence number or use the 1-Click Demo Verification below.")
            return render(request, 'licence_upload.html', {'profile': profile})

        # Format if standard 15-16 character Indian RTO format, else keep clean user input
        if len(cleaned_dl) >= 15 and cleaned_dl[2:4].isdigit() and cleaned_dl[4:8].isdigit():
            formatted_dl = f"{cleaned_dl[:2]}-{cleaned_dl[2:4]}-{cleaned_dl[4:8]}-{cleaned_dl[8:]}"
        else:
            formatted_dl = licence_number

        issue_date = None
        if issue_date_str:
            try:
                issue_date = datetime.strptime(issue_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        else:
            issue_date = date.today() - timedelta(days=365 * 2)

        expiry_date = None
        if expiry_date_str:
            try:
                expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        else:
            expiry_date = date.today() + timedelta(days=365 * 5)

        # Check expiry date in demo verification
        if expiry_date and expiry_date < date.today():
            profile.licence_number = formatted_dl
            profile.licence_issue_date = issue_date
            profile.licence_expiry_date = expiry_date
            profile.licence_status = 'Rejected'
            profile.rejection_reason = 'Demo Verification: Driving licence has expired.'
            profile.save()
            messages.error(request, "Demo Verification Check Failed: This driving licence has already expired. An active, non-expired driving licence is required.")
            return render(request, 'licence_upload.html', {'profile': profile})

        # Ensure demo date_of_birth is set for smooth eligibility testing
        if not profile.date_of_birth:
            profile.date_of_birth = date(1998, 5, 20)

        # In Demo Licence Verification mode: Instantly verify and approve
        profile.licence_number = formatted_dl
        profile.licence_issue_date = issue_date
        profile.licence_expiry_date = expiry_date
        if licence_file:
            profile.licence_image = licence_file

        profile.licence_status = 'Approved'
        profile.rejection_reason = ''
        profile.admin_notes = 'Demo Verification: Automatically verified and approved in Demo Mode.'
        profile.save()

        state_name = profile.rto_state or "State / Demo Authority"
        messages.success(request, f"Demo Licence Verification Successful! Licence ({formatted_dl} - {state_name}) has been verified and APPROVED instantly.")
        return redirect('licence_status')

    return render(request, 'licence_upload.html', {'profile': profile})

@login_required
def demo_licence_verify_view(request):
    """
    Demo Licence Verification Simulator:
    Allows instant 1-click verification of demo licences, simulating expired licences,
    or resetting licence status for test and demonstration purposes.
    """
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        action = request.POST.get('action', 'activate_valid')

        if action == 'activate_valid':
            demo_num = request.POST.get('demo_dl_number', 'DL-04-2023-DEMO8888')
            profile.licence_number = demo_num
            profile.licence_issue_date = date.today() - timedelta(days=365 * 3)
            profile.licence_expiry_date = date.today() + timedelta(days=365 * 10)
            if not profile.date_of_birth or (profile.age and profile.age < 25):
                profile.date_of_birth = date(1998, 5, 20)  # Age 28, qualifies for Normal & Premium
            profile.licence_status = 'Approved'
            profile.rejection_reason = ''
            profile.admin_notes = 'Demo Verification: 1-Click Instant Demo Verified'
            profile.save()
            messages.success(request, f"Demo Licence ({profile.licence_number}) verified and approved! You are eligible for all vehicle categories.")

        elif action == 'simulate_expired':
            profile.licence_number = 'DL-01-2015-EXPIRED'
            profile.licence_issue_date = date(2015, 1, 1)
            profile.licence_expiry_date = date.today() - timedelta(days=60)
            profile.licence_status = 'Rejected'
            profile.rejection_reason = 'Demo Verification: Driving licence has expired under RTO records.'
            profile.save()
            messages.warning(request, "Simulated Expired Demo Licence activated. Licence status set to Rejected.")

        elif action == 'simulate_pending':
            profile.licence_status = 'Pending'
            profile.rejection_reason = ''
            profile.admin_notes = 'Demo Verification: Simulated Pending Review'
            profile.save()
            messages.info(request, "Simulated Pending Verification mode activated.")

        elif action == 'reset':
            profile.licence_status = 'Not Uploaded'
            profile.licence_number = ''
            profile.licence_issue_date = None
            profile.licence_expiry_date = None
            profile.licence_image = None
            profile.rejection_reason = ''
            profile.admin_notes = ''
            profile.save()
            messages.info(request, "Demo licence reset to 'Not Uploaded'.")

    return redirect('licence_status')

@login_required
def licence_status_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'licence_status.html', {'profile': profile})

@login_required
def admin_toggle_licence(request, profile_id, action):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Permission denied.")
        return redirect('licence_status')

    profile = get_object_or_404(UserProfile, id=profile_id)
    if action == 'approve':
        profile.licence_status = 'Approved'
        profile.rejection_reason = ''
        messages.success(request, f"Indian Driving Licence for {profile.user.username} ({profile.licence_number} - {profile.rto_state or 'RTO'}) has been APPROVED & VERIFIED.")
    elif action == 'reject':
        profile.licence_status = 'Rejected'
        profile.rejection_reason = 'Document resolution insufficient or not recognized under Parivahan Sarathi records.'
        messages.warning(request, f"Licence for {profile.user.username} has been REJECTED.")
    elif action == 'reset':
        profile.licence_status = 'Pending'
        messages.info(request, f"Licence status reset to PENDING RTO Verification for {profile.user.username}.")
    
    profile.save()
    return redirect('licence_status')
