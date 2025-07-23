from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Date'
    )
    class Meta:
        model = Event
        fields = [
            'name', 'date', 'location', 'description', 'thumbnail',
            'event_type', 'sport_type', 'league'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hide sport_type and league unless event_type is 'sports'
        if self.instance and self.instance.event_type != 'sports':
            self.fields['sport_type'].widget = forms.HiddenInput()
            self.fields['league'].widget = forms.HiddenInput()