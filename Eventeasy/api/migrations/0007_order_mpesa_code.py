# Generated by Django 5.1.1 on 2024-10-07 18:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_order_event_type_order_paid'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='mpesa_code',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
