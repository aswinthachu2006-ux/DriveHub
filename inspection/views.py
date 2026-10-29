import uuid
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from bookings.models import Booking
from .models import Inspection, DamageReport

@login_required
def before_inspection_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if not (request.user == booking.user or request.user.is_staff):
        messages.error(request, "Permission denied.")
        return redirect('dashboard')

    inspection, _ = Inspection.objects.get_or_create(booking=booking, car=booking.car)

    if request.method == 'POST':
        inspection.inspector_name = request.POST.get('inspector_name', 'DriveHub Vehicle Specialist')
        inspection.before_odometer = int(request.POST.get('before_odometer', 12000))
        inspection.before_fuel_level = request.POST.get('before_fuel_level', '100% Full')
        inspection.before_exterior_condition = request.POST.get('before_exterior_condition', 'Pristine / Excellent')
        inspection.before_interior_clean = 'before_interior_clean' in request.POST
        inspection.before_spare_tire_toolkit = 'before_spare_tire_toolkit' in request.POST
        inspection.before_lights_electronics = 'before_lights_electronics' in request.POST
        inspection.before_notes = request.POST.get('before_notes', '')
        inspection.before_inspection_date = datetime.now()
        inspection.before_completed = True
        inspection.save()

        # Update booking status to Ongoing
        if booking.status == 'Confirmed':
            booking.status = 'Ongoing'
            booking.save()

        messages.success(request, f"Pre-Trip Handover Inspection completed for Booking #{booking.booking_id}!")
        return redirect('before_inspection', booking_id=booking.id)

    return render(request, 'before_inspection.html', {
        'booking': booking,
        'car': booking.car,
        'inspection': inspection,
    })

@login_required
def after_inspection_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if not (request.user == booking.user or request.user.is_staff):
        messages.error(request, "Permission denied.")
        return redirect('dashboard')

    inspection, _ = Inspection.objects.get_or_create(booking=booking, car=booking.car)

    if request.method == 'POST':
        after_odo = request.POST.get('after_odometer')
        if after_odo:
            inspection.after_odometer = int(after_odo)
        inspection.after_fuel_level = request.POST.get('after_fuel_level', '100% Full')
        inspection.after_exterior_condition = request.POST.get('after_exterior_condition', 'Good / Clean')
        inspection.damages_detected = (request.POST.get('damages_detected') == 'yes')
        inspection.after_notes = request.POST.get('after_notes', '')
        inspection.after_inspection_date = datetime.now()
        inspection.after_completed = True
        inspection.save()

        # If no damages or all damages settled, mark booking completed and car available
        booking.status = 'Completed'
        booking.save()
        booking.car.status = 'Available'
        booking.car.save()

        if inspection.damages_detected:
            messages.warning(request, "Return Inspection logged with damages. Please file or review the Damage Report below.")
        else:
            messages.success(request, f"Vehicle Return Inspection completed! Booking #{booking.booking_id} is marked as Completed.")

        return redirect('after_inspection', booking_id=booking.id)

    return render(request, 'after_inspection.html', {
        'booking': booking,
        'car': booking.car,
        'inspection': inspection,
    })

@login_required
def damage_report_view(request, inspection_id):
    inspection = get_object_or_404(Inspection, id=inspection_id)
    booking = inspection.booking
    if not (request.user == booking.user or request.user.is_staff):
        messages.error(request, "Permission denied.")
        return redirect('dashboard')

    if request.method == 'POST':
        title = request.POST.get('damage_title', 'Damage Report')
        dmg_type = request.POST.get('damage_type', 'Exterior Scratch')
        severity = request.POST.get('severity', 'Minor')
        cost = float(request.POST.get('estimated_cost', 2500.0))
        description = request.POST.get('description', '')
        image = request.FILES.get('damage_image')

        damage = DamageReport.objects.create(
            inspection=inspection,
            damage_title=title,
            damage_type=dmg_type,
            severity=severity,
            estimated_cost=cost,
            description=description,
            damage_image=image
        )

        inspection.damages_detected = True
        inspection.save()

        messages.warning(request, f"Damage Incident #{damage.id} recorded. Settlement is required.")
        return redirect('damage_details', damage_id=damage.id)

    return render(request, 'damage_report.html', {'inspection': inspection})

@login_required
def damage_details_view(request, damage_id):
    damage = get_object_or_404(DamageReport, id=damage_id)
    booking = damage.inspection.booking
    if not (request.user == booking.user or request.user.is_staff):
        messages.error(request, "Permission denied.")
        return redirect('dashboard')

    return render(request, 'damage_details.html', {'damage': damage})

@login_required
def damage_payment_view(request, damage_id):
    damage = get_object_or_404(DamageReport, id=damage_id)
    booking = damage.inspection.booking
    if not (request.user == booking.user or request.user.is_staff):
        messages.error(request, "Permission denied.")
        return redirect('dashboard')

    if request.method == 'POST':
        method = request.POST.get('payment_method', 'Credit/Debit Card')
        damage.payment_method = method
        damage.payment_status = 'Paid'
        damage.transaction_id = f"DHB-DMG-{uuid.uuid4().hex[:8].upper()}"
        damage.paid_at = datetime.now()
        damage.save()

        messages.success(request, f"Damage penalty of ₹{damage.estimated_cost} has been successfully settled!")
        return redirect('damage_details', damage_id=damage.id)

    return render(request, 'damage_payment.html', {'damage': damage})

# Create your views here.
