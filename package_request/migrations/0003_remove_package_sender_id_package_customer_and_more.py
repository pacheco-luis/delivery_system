# Generated by Django 4.2.3 on 2024-01-01 21:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
        ('package_request', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='package',
            name='sender_id',
        ),
        migrations.AddField(
            model_name='package',
            name='customer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.customer'),
        ),
        migrations.AddField(
            model_name='package',
            name='distance',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='package',
            name='driver',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.driver'),
        ),
        migrations.AddField(
            model_name='package',
            name='duration',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='package',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='package',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('picking', 'Picking'), ('delivering', 'Delivering'), ('completed', 'Completed'), ('canceled', 'Canceled')], default='pending', max_length=10),
        ),
    ]
