# Generated by Django 4.2.3 on 2023-11-14 15:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
        ('package_request', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='package',
            name='sender_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.customer'),
        ),
    ]
