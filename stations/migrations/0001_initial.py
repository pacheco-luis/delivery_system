# Generated by Django 4.2.3 on 2024-03-11 12:01

from django.db import migrations, models
import places.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Station',
            fields=[
                ('station_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=25)),
                ('address', places.fields.PlacesField(blank=True, max_length=255, verbose_name='station address')),
                ('station_radius', models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19)], default=1, verbose_name='station radius (Km)')),
            ],
            options={
                'db_table': 'Stations',
            },
        ),
    ]
