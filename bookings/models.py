import uuid
from django.db import models
from django.contrib.auth.models import User
from cars.models import Car

class Booking(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending Confirmation'),
        ('Confirmed', 'Confirmed'),
        ('Ongoing', 'Ongoing / In-Trip'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('Unpaid', 'Unpaid'),
        ('Paid', 'Paid'),
        ('Refunded', 'Refunded'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('Credit/Debit Card', 'Credit / Debit Card'),
        ('UPI / QR', 'UPI / Instant QR'),
        ('Net Banking', 'Net Banking'),
        ('Pay on Pickup', 'Pay on Vehicle Pickup'),
    ]

    booking_id = models.CharField(max_length=30, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='bookings')
    
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.IntegerField(default=1)
    
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2)
    rental_charge = models.DecimalField(max_digits=10, decimal_places=2)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=3000.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    pickup_location = models.CharField(max_length=150, default="DriveHub Flagship Hub, Downtown")
    dropoff_location = models.CharField(max_length=150, default="DriveHub Flagship Hub, Downtown")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Unpaid')
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, blank=True)
    transaction_id = models.CharField(max_length=80, blank=True)
    
    cancellation_reason = models.TextField(blank=True, null=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.booking_id:
            short_id = uuid.uuid4().hex[:6].upper()
            self.booking_id = f"DHB-{short_id}"
        
        # Calculate days & charges if not pre-computed
        if self.start_date and self.end_date:
            days = (self.end_date - self.start_date).days
            self.total_days = max(1, days)
            if not self.daily_rate and self.car:
                self.daily_rate = self.car.daily_rental_price
            self.rental_charge = self.daily_rate * self.total_days
            self.total_amount = self.rental_charge + self.security_deposit
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.booking_id} - {self.car.name} ({self.user.username})"

# Create your models here.
