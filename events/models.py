from django.db import models

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
    name = models.CharField(max_length=200)
    date = models.DateTimeField()
    location = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to='event_thumbnails/', blank=True, null=True)
    event_type = models.CharField(max_length=32, choices=EVENT_TYPE_CHOICES, default='sports')
    sport_type = models.CharField(max_length=32, choices=SPORTS_TYPE_CHOICES, blank=True, null=True)
    league = models.CharField(max_length=32, choices=LEAGUE_CHOICES, blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def tickets_sold(self):
        # Import here to avoid circular import
        from tickets.models import Ticket
        return Ticket.objects.filter(event=self, status='Active').count()

    @property
    def tickets_remaining(self):
        return self.total_tickets - self.tickets_sold
