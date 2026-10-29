from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'car', 'user', 'start_date', 'end_date', 'total_days', 'total_amount', 'status', 'payment_status')
    list_filter = ('status', 'payment_status', 'start_date', 'car__category')
    search_fields = ('booking_id', 'user__username', 'car__name', 'transaction_id')
    readonly_fields = ('booking_id', 'rental_charge', 'total_amount', 'created_at', 'updated_at')

# Register your models here.
