from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Ticket, TicketType
from events.models import Event
from django import forms
from django.utils import timezone
# import requests
# import base64
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Ticket purchase form
class TicketPurchaseForm(forms.ModelForm):
    phone = forms.CharField(
        label="M-Pesa Phone Number",
        max_length=13,
        help_text="Format: 2547XXXXXXXX"
    )

    class Meta:
        model = Ticket
        fields = ['seat', 'tickettype']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.event = kwargs.pop('event', None)
        super().__init__(*args, **kwargs)
        tickettype_qs = self.event.ticket_types.all() if self.event else TicketType.objects.none()
        self.fields['tickettype'].queryset = tickettype_qs

        # Dynamically set seat choices based on selected tickettype
        tickettype = None
        if self.data.get('tickettype'):
            try:
                tickettype = tickettype_qs.get(pk=self.data.get('tickettype'))
            except (TicketType.DoesNotExist, ValueError):
                pass
        elif self.initial.get('tickettype'):
            tickettype = self.initial['tickettype']

        if tickettype:
            all_seats = tickettype.get_seat_list()
            taken_seats = Ticket.objects.filter(
                event=self.event,
                tickettype=tickettype,
                status='Active'
            ).values_list('seat', flat=True)
            available_seats = [(s, s) for s in all_seats if s not in taken_seats]
            self.fields['seat'] = forms.ChoiceField(choices=available_seats, label="Seat")
        else:
            self.fields['seat'] = forms.ChoiceField(choices=[('', 'Select a ticket type first')], label="Seat")

        self.fields['seat'] = forms.CharField(widget=forms.HiddenInput(), required=True, label="Seat")

    def clean_seat(self):
        seat = self.cleaned_data['seat']
        tickettype = self.cleaned_data.get('tickettype')
        if self.user and self.event and tickettype:
            exists = Ticket.objects.filter(
                event=self.event,
                tickettype=tickettype,
                seat=seat,
                status='Active'
            ).exists()
            if exists:
                raise forms.ValidationError("This seat has already been booked.")
        return seat

    def clean_tickettype(self):
        tickettype = self.cleaned_data['tickettype']
        event = self.event
        sold = Ticket.objects.filter(event=event, tickettype=tickettype, status='Active').count()
        remaining = tickettype.total_available - sold
        if remaining <= 0:
            raise forms.ValidationError("This ticket type is sold out.")
        return tickettype

# def get_mpesa_access_token():
#     consumer_key = settings.MPESA_CONSUMER_KEY
#     consumer_secret = settings.MPESA_CONSUMER_SECRET
#     api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
#     r = requests.get(api_URL, auth=(consumer_key, consumer_secret))
#     return r.json().get('access_token')

# def lipa_na_mpesa_online(phone, amount, account_reference, transaction_desc, callback_url):
#     access_token = get_mpesa_access_token()
#     shortcode = settings.MPESA_SHORTCODE
#     passkey = settings.MPESA_PASSKEY
#     timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
#     data_to_encode = shortcode + passkey + timestamp
#     password = base64.b64encode(data_to_encode.encode()).decode()
#     api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
#     headers = {"Authorization": f"Bearer {access_token}"}
#     payload = {
#         "BusinessShortCode": shortcode,
#         "Password": password,
#         "Timestamp": timestamp,
#         "TransactionType": "CustomerPayBillOnline",
#         "Amount": amount,
#         "PartyA": phone,
#         "PartyB": shortcode,
#         "PhoneNumber": phone,
#         "CallBackURL": callback_url,
#         "AccountReference": account_reference,
#         "TransactionDesc": transaction_desc,
#     }
#     response = requests.post(api_url, json=payload, headers=headers)
#     return response.json()

@login_required
def ticket_purchase(request, event_id, tickettype_id):
    event_obj = get_object_or_404(Event, pk=event_id)
    ticket_types = []
    taken_seats_dict = {}
    for ttype in event_obj.ticket_types.all():
        sold = Ticket.objects.filter(event=event_obj, tickettype=ttype, status='Active').count()
        ttype.remaining = ttype.total_available - sold
        ticket_types.append(ttype)
        # Prepare taken seats for this ticket type
        taken_seats_dict[ttype.pk] = list(
            Ticket.objects.filter(event=event_obj, tickettype=ttype, status='Active').values_list('seat', flat=True)
        )

    available_seats_dict = {}
    for ttype in ticket_types:
        all_seats = ttype.get_seat_list()
        taken_seats = taken_seats_dict[ttype.pk]
        available_seats_dict[ttype.pk] = [s for s in all_seats if s not in taken_seats]

    if request.method == 'POST':
        form = TicketPurchaseForm(request.POST, event=event_obj, user=request.user)
        form.fields['tickettype'].queryset = event_obj.ticket_types.all()
        if form.is_valid():
            seats = request.POST.get('seat', '').split(',')
            quantity = int(request.POST.get('quantity', 1))
            tickettype = form.cleaned_data['tickettype']
            if len(seats) != quantity:
                form.add_error('seat', "Number of seats must match the quantity.")
            else:
                tickets_to_create = []
                purchase_time = timezone.now()
                for seat in seats:
                    ticket = Ticket(
                        user=request.user,
                        event=event_obj,
                        tickettype=tickettype,
                        seat=seat,
                        status='Active',
                        purchase_date=purchase_time
                    )
                    tickets_to_create.append(ticket)
                Ticket.objects.bulk_create(tickets_to_create)
                # Fetch the tickets just created
                tickets = Ticket.objects.filter(
                    user=request.user,
                    event=event_obj,
                    seat__in=seats,
                    purchase_date__gte=purchase_time
                )

                for ticket in tickets:
                    ticket.save()  # This will generate and save the QR code if not present

                ticket_ids = [t.pk for t in tickets]
                return redirect('ticket_confirm', ids=",".join(map(str, ticket_ids)))
    else:
        form = TicketPurchaseForm(event=event_obj, user=request.user)
        form.fields['tickettype'].queryset = event_obj.ticket_types.all()

    return render(request, 'tickets/ticket_purchase.html', {
        'form': form,
        'event': event_obj,
        'ticket_types': ticket_types,
        'taken_seats_dict': taken_seats_dict,  # Pass to template
        'available_seats_dict': available_seats_dict,
    })

@login_required
def ticket_list(request):
    tickets = Ticket.objects.filter(user=request.user).exclude(status='Cancelled').select_related('event').order_by('-purchase_date')
    return render(request, 'tickets/ticket_list.html', {'tickets': tickets, 'now': timezone.now()})

@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk, user=request.user)
    return render(request, 'tickets/ticket_detail.html', {'ticket': ticket})

@login_required
def ticket_confirm(request, ids):
    id_list = [int(pk) for pk in ids.split(',') if pk.isdigit()]
    tickets = Ticket.objects.filter(pk__in=id_list, user=request.user)
    return render(request, 'tickets/ticket_confirm.html', {'tickets': tickets})

@login_required
def ticket_cancel(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk, user=request.user)
    if request.method == 'POST':
        ticket.status = 'Cancelled'
        ticket.save()
        return redirect('ticket_list')
    return render(request, 'tickets/ticket_cancel.html', {'ticket': ticket})

@login_required
def cancelled_tickets(request):
    tickets = Ticket.objects.filter(user=request.user, status='Cancelled').select_related('event').order_by('-purchase_date')
    return render(request, 'tickets/cancelled_tickets.html', {'tickets': tickets, 'now': timezone.now()})

# @csrf_exempt
# def mpesa_callback(request):
#     if request.method == 'POST':
#         import json
#         data = json.loads(request.body)
#         # Process the payment result here
#         # For example, check if payment was successful and update ticket status
#         # Example: data['Body']['stkCallback']['ResultCode'] == 0 means success
#         # Save transaction details as needed
#         return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})
#     return JsonResponse({"ResultCode": 1, "ResultDesc": "Invalid request"}, status=400)
