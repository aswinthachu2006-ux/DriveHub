from django.urls import path
from . import views

urlpatterns = [
    path('before/<int:booking_id>/', views.before_inspection_view, name='before_inspection'),
    path('after/<int:booking_id>/', views.after_inspection_view, name='after_inspection'),
    path('damage-report/<int:inspection_id>/', views.damage_report_view, name='damage_report'),
    path('damage-details/<int:damage_id>/', views.damage_details_view, name='damage_details'),
    path('damage-payment/<int:damage_id>/', views.damage_payment_view, name='damage_payment'),
]
