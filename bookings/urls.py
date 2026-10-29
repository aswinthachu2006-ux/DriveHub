from django.urls import path
from . import views

urlpatterns = [
    path('book/<int:car_id>/', views.booking_view, name='booking'),
    path('confirm/<int:booking_id>/', views.booking_confirm_view, name='booking_confirm'),
    path('payment/<int:booking_id>/', views.payment_view, name='payment'),
    path('success/<int:booking_id>/', views.booking_success_view, name='booking_success'),
    path('details/<int:booking_id>/', views.booking_details_view, name='booking_details'),
    path('history/', views.booking_history_view, name='booking_history'),
    path('cancel/<int:booking_id>/', views.cancel_booking_view, name='cancel_booking'),
]
