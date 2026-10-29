from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Car

def normal_cars(request):
    cars = Car.objects.filter(category='Normal')
    query = request.GET.get('q')
    transmission = request.GET.get('transmission')
    fuel = request.GET.get('fuel')

    if query:
        cars = cars.filter(Q(name__icontains=query) | Q(brand__icontains=query))
    if transmission:
        cars = cars.filter(transmission=transmission)
    if fuel:
        cars = cars.filter(fuel_type=fuel)

    return render(request, 'normal_cars.html', {'cars': cars})

def premium_cars(request):
    cars = Car.objects.filter(category='Premium')
    query = request.GET.get('q')
    transmission = request.GET.get('transmission')
    fuel = request.GET.get('fuel')

    if query:
        cars = cars.filter(Q(name__icontains=query) | Q(brand__icontains=query))
    if transmission:
        cars = cars.filter(transmission=transmission)
    if fuel:
        cars = cars.filter(fuel_type=fuel)

    return render(request, 'premium_cars.html', {'cars': cars})

def car_details(request, pk):
    car = get_object_or_404(Car, pk=pk)
    return render(request, 'car_details.html', {
        'car': car,
    })

# Create your views here.
