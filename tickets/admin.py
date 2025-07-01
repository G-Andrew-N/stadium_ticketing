from django.contrib import admin
from .models import Ticket, TicketType

admin.site.register(Ticket)
admin.site.register(TicketType)
# Register your models here.
