from django.shortcuts import render, redirect
from django.contrib import messages
from cars.models import Car
from .models import ContactMessage
from django.db.models import Q

FLEET_GALLERY = [
    {'name': 'Aston Martin', 'image': 'astin martin.jpg'},
    {'name': 'Maruti Suzuki Baleno', 'image': 'baleno.jpg'},
    {'name': 'Mercedes-Benz', 'image': 'benz.jpg'},
    {'name': 'BMW', 'image': 'bmw.jpg'},
    {'name': 'Hyundai Creta', 'image': 'creta.jpg'},
    {'name': 'Land Rover Defender', 'image': 'defander.jpg'},
    {'name': 'Maruti Suzuki Ertiga', 'image': 'eartiga.jpg'},
    {'name': 'Toyota Innova', 'image': 'innova2.jpg'},
    {'name': 'Lamborghini', 'image': 'lamborghini.jpg'},
    {'name': 'Lexus', 'image': 'lexus.jpg'},
    {'name': 'Tata Safari', 'image': 'safari.jpg'},
    {'name': 'Maruti Suzuki Swift', 'image': 'swift.jpg'},
]

def home(request):
    cars = Car.objects.all()
    category = request.GET.get('category')
    transmission = request.GET.get('transmission')
    fuel = request.GET.get('fuel')
    query = request.GET.get('q')

    if category:
        cars = cars.filter(category=category)
    if transmission:
        cars = cars.filter(transmission=transmission)
    if fuel:
        cars = cars.filter(fuel_type=fuel)
    if query:
        cars = cars.filter(
            Q(name__icontains=query) |
            Q(brand__icontains=query) |
            Q(description__icontains=query)
        )

    return render(request, 'home.html', {
        'cars': cars,
        'fleet_gallery': FLEET_GALLERY,
    })

def about(request):
    return render(request, 'about.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '').strip()
        cleaned_phone = phone.replace(' ', '').replace('-', '')
        if cleaned_phone.isdigit() and len(cleaned_phone) == 10:
            phone = f"+91 {cleaned_phone}"
        subject = request.POST.get('subject')
        message_text = request.POST.get('message')

        if name and email and subject and message_text:
            ContactMessage.objects.create(
                name=name,
                email=email,
                phone=phone,
                subject=subject,
                message=message_text,
            )
            messages.success(request, "Thank you! Your message has been sent to our customer service team.")
            return redirect('contact')
        else:
            messages.error(request, "Please fill in all required fields.")

    return render(request, 'contact.html')

# Create your views here.
