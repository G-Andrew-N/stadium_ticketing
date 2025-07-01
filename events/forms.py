from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Date'
    )
    class Meta:
        model = Event
        fields = ['name', 'event_type', 'date', 'location', 'description', 'thumbnail']