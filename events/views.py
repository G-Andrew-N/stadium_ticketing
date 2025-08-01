from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Event
from .forms import EventForm
from tickets.models import Ticket, TicketType, TICKET_TYPE_CHOICES
from django.utils import timezone
from django.contrib.auth.models import User
from events.models import Event

import calendar
from datetime import date, datetime, timedelta
import json

def event_list(request):
    event_type = request.GET.get('type')
    q = request.GET.get('q', '')
    selected_sport_type = request.GET.get('sport_type', '')
    selected_league = request.GET.get('league', '')

    events = Event.objects.all()
    if event_type:
        events = events.filter(event_type=event_type)
    if q:
        events = events.filter(name__icontains=q) | events.filter(location__icontains=q)
    # Filter sports events by sport_type and league
    if event_type == 'sports':
        if selected_sport_type:
            events = events.filter(sport_type=selected_sport_type)
        if selected_league:
            events = events.filter(league=selected_league)

    # Group events by type for display
    from collections import OrderedDict
    grouped_events = OrderedDict()
    for key, label in Event.EVENT_TYPE_CHOICES:
        grouped_events[label] = events.filter(event_type=key)

    # Only show sport types and leagues for sports events
    sport_type_choices = Event.objects.filter(event_type='sports').values_list('sport_type', flat=True).distinct()
    league_choices = Event.objects.filter(event_type='sports').values_list('league', flat=True).distinct()

    # Convert to (key, label) tuples using model choices for display
    sport_type_display = dict(Event.SPORTS_TYPE_CHOICES)
    league_display = dict(Event.LEAGUE_CHOICES)
    sport_type_choices = [(key, sport_type_display.get(key, key)) for key in sport_type_choices if key]
    league_choices = [(key, league_display.get(key, key)) for key in league_choices if key]

    context = {
        'grouped_events': grouped_events,
        'event_type_choices': Event.EVENT_TYPE_CHOICES,
        'selected_type': event_type,
        'selected_sport_type': selected_sport_type,
        'selected_league': selected_league,
        'q': q,
        'sport_type_choices': sport_type_choices,
        'league_choices': league_choices,
    }
    return render(request, 'events/event_list.html', context)

def event_detail(request, pk):
    event_obj = get_object_or_404(Event, pk=pk)
    ticket_types = event_obj.ticket_types.all()
    ticket_type_data = []
    for tt in ticket_types:
        sold = Ticket.objects.filter(event=event_obj, status='Active', tickettype=tt).count()
        remaining = tt.total_available - sold
        ticket_type_data.append({
            'type': tt,
            'sold': sold,
            'remaining': remaining,
        })
    return render(request, 'events/event_detail.html', {
        'event': event_obj,
        'ticket_type_data': ticket_type_data,
    })

def event_form(request, pk=None):
    if pk:
        event_obj = get_object_or_404(Event, pk=pk)
    else:
        event_obj = None

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event_obj)
        if form.is_valid():
            saved_event = form.save()
            # Remove old ticket types if editing
            if event_obj:
                TicketType.objects.filter(event=saved_event).delete()
            # Process ticket types from POST
            selected_types = request.POST.getlist('ticket_types')
            for key, label in TICKET_TYPE_CHOICES:
                if key in selected_types:
                    price = request.POST.get(f'price_{key}', '0')
                    qty = request.POST.get(f'qty_{key}', '0')
                    seats = request.POST.get(f'seats_{key}')  # This is the generated seat list, e.g. B1,B2,B3,...
                    # Create TicketType with seats
                    TicketType.objects.create(
                        event=saved_event,
                        name=key,
                        price=price,
                        total_available=qty,
                        seats=seats
                    )
            return redirect('event_detail', pk=saved_event.pk)
    else:
        form = EventForm(instance=event_obj)

    return render(request, 'events/event_form.html', {
        'form': form,
        'event': event_obj,
        'TICKET_TYPE_CHOICES': TICKET_TYPE_CHOICES,
    })

def event_edit(request, pk):
    event = get_object_or_404(Event, pk=pk)
    ticket_data = getattr(event, 'ticket_data', {})
    if isinstance(ticket_data, str):
        try:
            saved_ticket_types = json.loads(ticket_data)
        except Exception:
            saved_ticket_types = {}
    else:
        saved_ticket_types = ticket_data
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('event_detail', pk=event.pk)
    else:
        form = EventForm(instance=event)

    # Build saved_ticket_types from TicketType model
    saved_ticket_types = {}
    for tt in event.ticket_types.all():
        saved_ticket_types[tt.name] = {
            'price': tt.price,
            'quantity': tt.total_available
        }

    return render(request, 'events/event_form.html', {
        'form': form,
        'TICKET_TYPE_CHOICES': Event.EVENT_TYPE_CHOICES,
        'saved_ticket_types': saved_ticket_types,
    })

def event_confirm_delete(request, pk):
    event_obj = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        event_obj.delete()
        return redirect('event_list')
    return render(request, 'events/event_confirm_delete.html', {'event': event_obj})

def event_calendar(request):
    today = date.today()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    month_name = calendar.month_name[month]
    week_days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

    cal = calendar.Calendar()
    month_days = cal.monthdatescalendar(year, month)
    calendar_matrix = []
    for week in month_days:
        week_list = []
        for day in week:
            day_events = Event.objects.filter(date__date=day) if day.month == month else []
            week_list.append({
                'day': day.day if day.month == month else '',
                'events': day_events
            })
        calendar_matrix.append(week_list)

    context = {
        'month': month,  # <-- Add this line
        'month_name': month_name,
        'year': year,
        'week_days': week_days,
        'calendar': calendar_matrix,
        'calendar_module': calendar,  # If you want to use calendar.month_name in template
    }
    return render(request, 'events/event_calendar.html', context)

def admin_dashboard(request):
    total_events = Event.objects.count()
    total_tickets = Ticket.objects.filter(status='Active').count()
    total_users = User.objects.filter(is_active=True, is_superuser=False).count()
    upcoming_events = Event.objects.filter(date__gte=timezone.now()).count()
    return render(request, 'events/admin_dashboard.html', {
        'total_events': total_events,
        'total_tickets': total_tickets,
        'total_users': total_users,
        'upcoming_events': upcoming_events,
    })

@login_required
def user_dashboard(request):
    tickets = Ticket.objects.filter(user=request.user).select_related('event').order_by('-purchase_date')
    return render(request, 'events/user_dashboard.html', {
        'tickets': tickets,
        'now': timezone.now(),
    })

