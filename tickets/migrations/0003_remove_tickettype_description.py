# Generated by Django 5.1.6 on 2025-06-23 14:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0002_tickettype'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tickettype',
            name='description',
        ),
    ]
