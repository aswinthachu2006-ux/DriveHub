from django.contrib import admin
from .models import UserProfile

@admin.action(description="Approve selected user driving licences")
def approve_licences(modeladmin, request, queryset):
    queryset.update(licence_status='Approved', rejection_reason='')

@admin.action(description="Reject selected user driving licences")
def reject_licences(modeladmin, request, queryset):
    queryset.update(licence_status='Rejected', rejection_reason='Administrative review failed: please re-upload clear photo.')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'licence_status', 'licence_number', 'age', 'licence_expiry_date', 'uploaded_at')
    list_filter = ('licence_status', 'licence_expiry_date')
    search_fields = ('user__username', 'user__email', 'licence_number', 'phone')
    actions = [approve_licences, reject_licences]


# Register your models here.
