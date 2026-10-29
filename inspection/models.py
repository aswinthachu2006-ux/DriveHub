from django.db import models
from bookings.models import Booking
from cars.models import Car

class Inspection(models.Model):
    FUEL_CHOICES = [
        ('100% Full', '100% Full Tank'),
        ('75%', '75% Tank'),
        ('50%', '50% Tank'),
        ('25%', '25% Tank'),
        ('Reserve', 'Reserve Level'),
    ]

    CONDITION_CHOICES = [
        ('Pristine / Excellent', 'Pristine / Excellent'),
        ('Good / Clean', 'Good / Clean'),
        ('Minor Wear & Tear', 'Minor Wear & Tear'),
        ('Scratches / Blemishes', 'Scratches / Blemishes'),
        ('Damaged', 'Damaged'),
    ]

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='inspection')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='inspections')
    inspector_name = models.CharField(max_length=100, default="DriveHub Vehicle Specialist")

    # Before Handover Inspection
    before_odometer = models.IntegerField(default=12000, help_text="Odometer reading in KM")
    before_fuel_level = models.CharField(max_length=30, choices=FUEL_CHOICES, default='100% Full')
    before_exterior_condition = models.CharField(max_length=40, choices=CONDITION_CHOICES, default='Pristine / Excellent')
    before_interior_clean = models.BooleanField(default=True, verbose_name="Interior Vacuumed & Clean")
    before_spare_tire_toolkit = models.BooleanField(default=True, verbose_name="Spare Tire & Toolkit Present")
    before_lights_electronics = models.BooleanField(default=True, verbose_name="Headlights, Indicators & AC Operational")
    before_notes = models.TextField(blank=True, default="Vehicle sanitized, all fluid levels topped up. No pre-existing defects observed.")
    before_inspection_date = models.DateTimeField(null=True, blank=True)
    before_completed = models.BooleanField(default=False)

    # After Return Inspection
    after_odometer = models.IntegerField(null=True, blank=True, help_text="Return odometer reading in KM")
    after_fuel_level = models.CharField(max_length=30, choices=FUEL_CHOICES, null=True, blank=True)
    after_exterior_condition = models.CharField(max_length=40, choices=CONDITION_CHOICES, null=True, blank=True)
    after_interior_clean = models.BooleanField(default=True, verbose_name="Interior Returned in Clean Condition")
    after_notes = models.TextField(blank=True)
    after_inspection_date = models.DateTimeField(null=True, blank=True)
    after_completed = models.BooleanField(default=False)
    damages_detected = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Inspection for Booking #{self.booking.booking_id} ({self.car.name})"

    @property
    def total_kms_driven(self):
        if self.before_odometer and self.after_odometer:
            return max(0, self.after_odometer - self.before_odometer)
        return 0


class DamageReport(models.Model):
    DAMAGE_TYPES = [
        ('Exterior Scratch', 'Exterior Scratch'),
        ('Body Dent / Bumper Damage', 'Body Dent / Bumper Damage'),
        ('Glass / Windshield / Mirror Crack', 'Glass / Windshield / Mirror Crack'),
        ('Wheel / Rim Scuff or Tire Puncture', 'Wheel / Rim Scuff or Tire Puncture'),
        ('Interior Upholstery Stain / Tear', 'Interior Upholstery Stain / Tear'),
        ('Mechanical / Electrical Defect', 'Mechanical / Electrical Defect'),
        ('Other Penalty', 'Other Penalty'),
    ]

    SEVERITY_CHOICES = [
        ('Minor', 'Minor (Light surface mark)'),
        ('Moderate', 'Moderate (Requires buffing / spot paint)'),
        ('Severe', 'Severe (Requires panel replacement / bodywork)'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending Settlement'),
        ('Paid', 'Paid & Settled'),
        ('Waived', 'Waived under Insurance'),
    ]

    inspection = models.ForeignKey(Inspection, on_delete=models.CASCADE, related_name='damage_reports')
    damage_title = models.CharField(max_length=150, help_text="e.g. Scuffed passenger rear bumper")
    damage_type = models.CharField(max_length=60, choices=DAMAGE_TYPES, default='Exterior Scratch')
    severity = models.CharField(max_length=30, choices=SEVERITY_CHOICES, default='Minor')
    description = models.TextField(help_text="Detailed note of the damage location, dimensions, and cause.")
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, default=2500.00)
    damage_image = models.ImageField(upload_to='damages/', blank=True, null=True)
    
    payment_status = models.CharField(max_length=30, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    payment_method = models.CharField(max_length=50, blank=True)
    transaction_id = models.CharField(max_length=80, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    reported_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.damage_title} - ₹{self.estimated_cost} ({self.payment_status})"

# Create your models here.
