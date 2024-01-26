# Generated by Django 4.2.3 on 2024-01-25 13:49

from django.db import migrations, models
import phonenumber_field.modelfields
import places.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Package',
            fields=[
                ('package_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('sender_phone', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region='TW')),
                ('sender_address', places.fields.PlacesField(blank=True, max_length=255)),
                ('recipient_name', models.CharField(max_length=200)),
                ('recipient_phone', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region='TW')),
                ('recipient_address', places.fields.PlacesField(blank=True, max_length=255)),
                ('package_description', models.CharField(max_length=200)),
                ('fragile', models.BooleanField()),
                ('estimate_package_weight', models.CharField(choices=[('<2', '<2'), ('2-5', '2-5'), ('5-10', '5-10'), ('>10', '>10')], max_length=5)),
                ('order_date', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('picking', 'Picking'), ('delivering', 'Delivering'), ('completed', 'Completed'), ('canceled', 'Canceled')], default='pending', max_length=10)),
                ('duration', models.IntegerField(blank=True, default=0, null=True)),
                ('distance', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True)),
                ('price', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True)),
            ],
            options={
                'db_table': 'Packages',
            },
        ),
    ]
