from django.urls import path
from . import views

urlpatterns = [
    path('normal/', views.normal_cars, name='normal_cars'),
    path('premium/', views.premium_cars, name='premium_cars'),
    path('<int:pk>/', views.car_details, name='car_details'),
]
