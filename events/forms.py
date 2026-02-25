from django import forms
from datetime import datetime
from django.utils import timezone
from .models import Event

class EventForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Date'
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        label='Start Time'
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        label='End Time'
    )

    class Meta:
        model = Event
        fields = [
            'name', 'date', 'start_time', 'end_time', 'location', 'description', 'thumbnail',
            'event_type', 'sport_type', 'league'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hide sport_type and league unless event_type is 'sports'
        if self.instance and self.instance.event_type != 'sports':
            self.fields['sport_type'].widget = forms.HiddenInput()
            self.fields['league'].widget = forms.HiddenInput()

        if self.instance and self.instance.pk:
            self.initial.setdefault('date', self.instance.date.date())
            self.initial.setdefault('start_time', self.instance.start_time)
            self.initial.setdefault('end_time', self.instance.end_time)

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time and end_time <= start_time:
            self.add_error('end_time', 'End time must be later than start time.')

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        event_date = self.cleaned_data.get('date')
        start_time = self.cleaned_data.get('start_time')

        if event_date and start_time:
            combined_start = datetime.combine(event_date, start_time)
            if timezone.is_naive(combined_start):
                combined_start = timezone.make_aware(combined_start, timezone.get_current_timezone())
            instance.date = combined_start

        if commit:
            instance.save()
            self.save_m2m()

        return instance