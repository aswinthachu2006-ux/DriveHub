from django.contrib import admin
from .models import Inspection, DamageReport

class DamageReportInline(admin.TabularInline):
    model = DamageReport
    extra = 0

@admin.register(Inspection)
class InspectionAdmin(admin.ModelAdmin):
    list_display = ('booking', 'car', 'before_completed', 'after_completed', 'damages_detected', 'created_at')
    list_filter = ('before_completed', 'after_completed', 'damages_detected')
    search_fields = ('booking__booking_id', 'car__name', 'inspector_name')
    inlines = [DamageReportInline]

@admin.register(DamageReport)
class DamageReportAdmin(admin.ModelAdmin):
    list_display = ('damage_title', 'inspection', 'damage_type', 'severity', 'estimated_cost', 'payment_status')
    list_filter = ('severity', 'payment_status', 'damage_type')
    search_fields = ('damage_title', 'description', 'transaction_id')

# Register your models here.
