from django.shortcuts import render
from events.models import Event

def home(request):
    events = Event.objects.order_by('date')[:5]
    return render(request, 'stadium_ticketing/home.html', {'events': events})

def about(request):
    return render(request, 'stadium_ticketing/about.html')

def contact(request):
    return render(request, 'stadium_ticketing/contact.html')

def custom_404(request, exception):
    return render(request, '404.html', status=404)