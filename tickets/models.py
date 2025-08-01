from django.db import models
from django.contrib.auth.models import User
from events.models import Event
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

TICKET_TYPE_CHOICES = [
        ('VVIP', 'VVIP'),
        ('VIP', 'VIP'),
        ('Executive', 'Executive / Corporate Box'),
        ('Gold', 'Gold'),
        ('Silver', 'Silver'),
        ('Bronze', 'Bronze / Standard'),
        ('Economy', 'Economy / Regular'),
        ('Early Bird', 'Early Bird'),
        ('Group', 'Group / Family Pass'),
        ('Student', 'Student / Youth / Child Ticket'),
        ('Season', 'Season Pass'),
        ('All Access', 'All-Access Pass'),
        ('Press', 'Press / Media Pass'),
        ('Backstage', 'Backstage / Meet & Greet Pass'),
        ('Disabled', 'Disabled / Accessibility Ticket'),
    ]
class Ticket(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Cancelled', 'Cancelled'),
        ('Used', 'Used'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tickets')
    tickettype = models.ForeignKey('TicketType', on_delete=models.CASCADE, related_name='tickets', null=True, blank=True)
    seat = models.CharField(max_length=50)
    purchase_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    qr_code_url = models.URLField(blank=True, null=True)  # Optional: for QR code image
    qr_code_image = models.ImageField(upload_to='ticket_qrcodes/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.event.name} - {self.seat} ({self.status})"

    def generate_qr_code(self):
        data = f"Ticket:{self.pk}|User:{self.user.username}|Event:{self.event.name}|Seat:{self.seat}"
        qr = qrcode.make(data)
        buffer = BytesIO()
        qr.save(buffer, format='PNG')
        filename = f"ticket_{self.pk}_qr.png"
        self.qr_code_image.save(filename, ContentFile(buffer.getvalue()), save=False)
        buffer.close()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.qr_code_image:
            self.generate_qr_code()
            super().save(update_fields=['qr_code_image'])

class TicketType(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='ticket_types')
    name = models.CharField(max_length=50, choices=TICKET_TYPE_CHOICES)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    total_available = models.PositiveIntegerField(default=0)
    seats = models.CharField(max_length=500, blank=True, help_text="Comma-separated seat numbers, e.g. A1,A2,A3")

    def __str__(self):
        return f"{self.event.name} - {self.get_name_display()}"

    def get_seat_list(self):
        return [s.strip() for s in self.seats.split(',') if s.strip()]
