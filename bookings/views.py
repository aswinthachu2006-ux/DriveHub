import uuid
from decimal import Decimal
from datetime import datetime, date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from cars.models import Car
from inspection.models import Inspection
from .models import Booking

@login_required
def booking_view(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    profile = getattr(request.user, 'profile', None)
    # Demo Mode: Real-time licence verification blocker is removed to allow seamless direct bookings.
    if profile and profile.licence_status != 'Approved':
        messages.info(request, "Demo Mode: Booking initiated without real-time licence blocker. You can complete demo licence verification anytime in your profile.")

    if request.method == 'POST':
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        pickup_loc = request.POST.get('pickup_location', 'DriveHub Flagship Hub, Downtown Metro')
        dropoff_loc = request.POST.get('dropoff_location', 'DriveHub Flagship Hub, Downtown Metro')

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            messages.error(request, "Please enter valid pickup and return dates.")
            return render(request, 'booking.html', {'car': car})

        if start_date < date.today():
            messages.error(request, "Pickup date cannot be in the past.")
            return render(request, 'booking.html', {'car': car})

        if end_date <= start_date:
            messages.error(request, "Return date must be strictly after pickup date.")
            return render(request, 'booking.html', {'car': car})

        total_days = (end_date - start_date).days
        daily_rate = car.daily_rental_price
        rental_charge = daily_rate * total_days
        security_deposit = Decimal("3000.00") if car.category == 'Normal' else Decimal("10000.00")
        total_amount = rental_charge + security_deposit

        booking = Booking.objects.create(
            user=request.user,
            car=car,
            start_date=start_date,
            end_date=end_date,
            total_days=total_days,
            daily_rate=daily_rate,
            rental_charge=rental_charge,
            security_deposit=security_deposit,
            total_amount=total_amount,
            pickup_location=pickup_loc,
            dropoff_location=dropoff_loc,
            status='Pending',
            payment_status='Unpaid'
        )

        # Initialize Inspection record
        Inspection.objects.get_or_create(booking=booking, car=car)

        return redirect('booking_confirm', booking_id=booking.id)

    return render(request, 'booking.html', {
        'car': car,
    })

@login_required
def booking_confirm_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'booking_confirm.html', {'booking': booking})

@login_required
def payment_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if request.method == 'POST':
        method = request.POST.get('payment_method', 'Credit/Debit Card')
        booking.payment_method = method
        booking.payment_status = 'Paid'
        booking.status = 'Confirmed'
        booking.transaction_id = f"DHB-TXN-{uuid.uuid4().hex[:8].upper()}"
        booking.save()

        # Update car status to rented
        booking.car.status = 'Rented'
        booking.car.save()

        messages.success(request, f"Payment successful! Booking #{booking.booking_id} is confirmed.")
        return redirect('booking_success', booking_id=booking.id)

    return render(request, 'payment.html', {'booking': booking})

@login_required
def booking_success_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'booking_success.html', {'booking': booking})

@login_required
def booking_details_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if not (request.user == booking.user or request.user.is_staff):
        messages.error(request, "Permission denied.")
        return redirect('dashboard')
    return render(request, 'booking_details.html', {'booking': booking})

@login_required
def booking_history_view(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    status_filter = request.GET.get('status')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    return render(request, 'booking_history.html', {'bookings': bookings})

@login_required
def cancel_booking_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if request.method == 'POST':
        reason_preset = request.POST.get('reason_preset', '')
        custom_reason = request.POST.get('cancellation_reason', '')
        full_reason = f"{reason_preset}. {custom_reason}".strip()

        booking.status = 'Cancelled'
        if booking.payment_status == 'Paid':
            booking.payment_status = 'Refunded'
        booking.cancellation_reason = full_reason
        booking.cancelled_at = datetime.now()
        booking.save()

        # Make car available again
        booking.car.status = 'Available'
        booking.car.save()

        messages.info(request, f"Booking #{booking.booking_id} has been cancelled and refunded.")
        return redirect('booking_history')

    return render(request, 'cancellation.html', {'booking': booking})

# Create your views here.
