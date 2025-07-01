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
        super().__init__(*args, **kwargs)

    def clean_seat(self):
        seat = self.cleaned_data['seat']
        if self.event:
            if Ticket.objects.filter(event=self.event, seat=seat, status='Active').exists():
                raise forms.ValidationError("This seat has already been taken. Please choose another seat.")
        return seat