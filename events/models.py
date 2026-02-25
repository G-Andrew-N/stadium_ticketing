from django.db import models
from django.utils import timezone
from datetime import datetime, time

# Create your models here.

class Event(models.Model):
    EVENT_TYPE_CHOICES = [
        ('sports', 'Sports Events'),
        ('entertainment', 'Entertainment Events'),
        ('civic', 'Civic and Political Events'),
        ('educational', 'Educational and Institutional Events'),
        ('corporate', 'Corporate and Business Events'),
        ('religious', 'Religious and Spiritual Events'),
        ('recreational', 'Recreational and Community Events'),
        ('esports', 'E-sports and Virtual Events'),
    ]
    SPORTS_TYPE_CHOICES = [
        ('football', 'Football'),
        ('basketball', 'Basketball'),
        ('athletics', 'Athletics'),
        ('rugby', 'Rugby'),
        ('tennis', 'Tennis'),
        # Add more as needed
    ]
    LEAGUE_CHOICES = [
        ('premier_league', 'Premier League'),
        ('national_league', 'National League'),
        ('champions_league', 'Champions League'),
        # Add more as needed
    ]
    LOCATION_CHOICES = [
        ('ol_kalou', 'Ol Kalou Stadium'),
        ('kararani', 'Kararani Stadium (Ndunyu Njeru)'),
    ]
    name = models.CharField(max_length=200)
    date = models.DateTimeField()
    start_time = models.TimeField(default=time(9, 0))
    end_time = models.TimeField(default=time(17, 0))
    location = models.CharField(max_length=32, choices=LOCATION_CHOICES, default='ol_kalou')
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to='event_thumbnails/', blank=True, null=True)
    event_type = models.CharField(max_length=32, choices=EVENT_TYPE_CHOICES, default='sports')
    sport_type = models.CharField(max_length=32, choices=SPORTS_TYPE_CHOICES, blank=True, null=True)
    league = models.CharField(max_length=32, choices=LEAGUE_CHOICES, blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def end_datetime(self):
        end_dt = datetime.combine(self.date.date(), self.end_time)
        if timezone.is_naive(end_dt):
            end_dt = timezone.make_aware(end_dt, timezone.get_current_timezone())
        return end_dt

    @property
    def is_over(self):
        return timezone.now() > self.end_datetime

    @property
    def tickets_sold(self):
        # Import here to avoid circular import
        from tickets.models import Ticket
        return Ticket.objects.filter(event=self, status='Active').count()

    @property
    def tickets_remaining(self):
        return self.total_tickets - self.tickets_sold
