from django.contrib import admin
from .models import Car

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category', 'daily_rental_price', 'status', 'minimum_age', 'transmission', 'fuel_type')
    list_filter = ('category', 'status', 'transmission', 'fuel_type', 'brand')
    search_fields = ('name', 'brand', 'registration_number', 'description')
    list_editable = ('status', 'daily_rental_price')
    fieldsets = (
        ('Vehicle Overview', {
            'fields': ('name', 'brand', 'category', 'model_year', 'registration_number')
        }),
        ('Specifications & Rental Rates', {
            'fields': ('daily_rental_price', 'minimum_age', 'seating_capacity', 'transmission', 'fuel_type', 'mileage', 'status')
        }),
        ('Visuals & Features', {
            'fields': ('image', 'image_url', 'description', 'features')
        }),
    )

# Register your models here.
