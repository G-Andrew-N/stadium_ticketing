from django import forms
from .models import Ticket, TicketType

class TicketPurchaseForm(forms.Form):
    tickettype = forms.ModelChoiceField(queryset=TicketType.objects.none(), label="Seat Category")
    seat = forms.IntegerField(
        label="Seat Number",
        min_value=0,
        max_value=10000,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter seat number (0-10000)'})
    )
    phone = forms.CharField(
        label="M-Pesa Phone Number",
        max_length=13,
        help_text="Format: 2547XXXXXXXX"
    )

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_seat(self):
        seat = self.cleaned_data['seat']
        tickettype = self.cleaned_data.get('tickettype')
        if self.event and self.user and tickettype:
            # Prevent any user from picking a taken seat
            if Ticket.objects.filter(event=self.event, seat=seat, status='Active').exists():
                raise forms.ValidationError("This seat has already been taken. Please choose another seat.")
            # Prevent this user from picking the same seat for this event and tickettype
            if Ticket.objects.filter(event=self.event, seat=seat, user=self.user, tickettype=tickettype, status='Active').exists():
                raise forms.ValidationError("You have already purchased this seat for this event.")
        return seat