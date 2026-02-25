from datetime import time
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0007_alter_event_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='start_time',
            field=models.TimeField(default=time(9, 0)),
        ),
        migrations.AddField(
            model_name='event',
            name='end_time',
            field=models.TimeField(default=time(17, 0)),
        ),
    ]
