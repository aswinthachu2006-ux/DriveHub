from django.db import models

class Car(models.Model):
    CATEGORY_CHOICES = [
        ('Normal', 'Normal Car'),
        ('Premium', 'Premium Car'),
    ]

    TRANSMISSION_CHOICES = [
        ('Automatic', 'Automatic'),
        ('Manual', 'Manual'),
    ]

    FUEL_CHOICES = [
        ('Petrol', 'Petrol'),
        ('Diesel', 'Diesel'),
        ('Electric', 'Electric'),
        ('Hybrid', 'Hybrid'),
    ]

    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Rented', 'Currently Rented'),
        ('Maintenance', 'Under Maintenance'),
    ]

    name = models.CharField(max_length=120, help_text="e.g. BMW M4 Competition, Toyota Camry")
    brand = models.CharField(max_length=60, help_text="e.g. BMW, Toyota, Mercedes-Benz, Audi")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Normal')
    model_year = models.IntegerField(default=2024)
    registration_number = models.CharField(max_length=40, unique=True)
    seating_capacity = models.IntegerField(default=5)
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES, default='Automatic')
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES, default='Petrol')
    daily_rental_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Rental rate per day (₹)")
    image = models.ImageField(upload_to='cars/', blank=True, null=True)
    image_url = models.CharField(max_length=500, blank=True, help_text="Direct or static image URL fallback")
    description = models.TextField(help_text="Detailed overview of the vehicle.")
    features = models.TextField(help_text="Comma-separated key features: Apple CarPlay, Sunroof, 360 Camera, etc.", blank=True)
    mileage = models.CharField(max_length=50, default="15 km/l", help_text="e.g. 18 km/l or 400 km range")
    minimum_age = models.IntegerField(default=21, help_text="Eligibility age check (21 for normal, 25 for premium)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-category', 'daily_rental_price']

    def __str__(self):
        return f"{self.brand} {self.name} ({self.category}) - ₹{self.daily_rental_price}/day"

    def get_features_list(self):
        if self.features:
            return [f.strip() for f in self.features.split(',') if f.strip()]
        return []

    def get_image_url(self):
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return "/static/images/car-placeholder.svg"

# Create your models here.
