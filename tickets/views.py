from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Ticket, TicketType
from events.models import Event
from django import forms
from django.utils import timezone
import requests
import base64
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
        fields = ['seat', 'tickettype']  # Do NOT add 'phone' here, since it's not in the model

def get_mpesa_access_token():
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    r = requests.get(api_URL, auth=(consumer_key, consumer_secret))
    return r.json().get('access_token')

def lipa_na_mpesa_online(phone, amount, account_reference, transaction_desc, callback_url):
    access_token = get_mpesa_access_token()
    shortcode = settings.MPESA_SHORTCODE
    passkey = settings.MPESA_PASSKEY
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    data_to_encode = shortcode + passkey + timestamp
    password = base64.b64encode(data_to_encode.encode()).decode()
    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": f"Bearer {access_token}"}
    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": shortcode,
        "PhoneNumber": phone,
        "CallBackURL": callback_url,
        "AccountReference": account_reference,
        "TransactionDesc": transaction_desc,
    }
    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()

@login_required
def ticket_list(request):
    tickets = Ticket.objects.filter(user=request.user).select_related('event').order_by('-purchase_date')
    return render(request, 'tickets/ticket_list.html', {'tickets': tickets, 'now': timezone.now()})

@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk, user=request.user)
    return render(request, 'tickets/ticket_detail.html', {'ticket': ticket})

@login_required
def ticket_purchase(request, event_id, tickettype_id):
    event_obj = get_object_or_404(Event, pk=event_id)
    ticket_types = []
    for ttype in event_obj.ticket_types.all():
        sold = Ticket.objects.filter(event=event_obj, tickettype=ttype, status='Active').count()
        ttype.remaining = ttype.total_available - sold
        ticket_types.append(ttype)

    if request.method == 'POST':
        form = TicketPurchaseForm(request.POST)
        form.fields['tickettype'].queryset = event_obj.ticket_types.all()
        if form.is_valid():
            ticket_type = get_object_or_404(TicketType, pk=tickettype_id)
            amount = int(ticket_type.price)
            phone = form.cleaned_data['phone']
            seat = form.cleaned_data['seat']

            # Initiate M-Pesa STK Push
            resp = lipa_na_mpesa_online(
                phone=phone,
                amount=amount,
                account_reference=f"{event_obj.name}",
                transaction_desc=f"Ticket for {event_obj.name}",
                callback_url=settings.MPESA_CALLBACK_URL
            )
            if resp.get('ResponseCode') == '0':
                # Save a pending ticket or payment record here if you wish
                return render(request, 'tickets/mpesa_pending.html', {'phone': phone})
            else:
                form.add_error(None, "M-Pesa payment initiation failed. Please try again.")
    else:
        form = TicketPurchaseForm()
        form.fields['tickettype'].queryset = event_obj.ticket_types.all()

    return render(request, 'tickets/ticket_purchase.html', {
        'form': form,
        'event': event_obj,
        'ticket_types': ticket_types,
    })

@login_required
def ticket_confirm(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk, user=request.user)
    return render(request, 'tickets/ticket_confirm.html', {'ticket': ticket})

@login_required
def ticket_cancel(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk, user=request.user)
    if request.method == 'POST':
        ticket.status = 'Cancelled'
        ticket.save()
        return redirect('ticket_list')
    return render(request, 'tickets/ticket_cancel.html', {'ticket': ticket})

@csrf_exempt
def mpesa_callback(request):
    import json
    data = json.loads(request.body)
    # Parse data and verify payment
    # If successful, mark ticket as paid/active and notify user
    # Example: data['Body']['stkCallback']['ResultCode'] == 0 means success
    return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})
