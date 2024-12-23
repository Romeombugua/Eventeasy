# Generated by Django 5.1.1 on 2024-11-01 09:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_order_taken_by_provider'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='mpesa_code',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AlterField(
            model_name='useraccount',
            name='role',
            field=models.CharField(choices=[('CLIENT', 'Client'), ('PROVIDER', 'Provider')], default='CLIENT', max_length=20),
        ),
    ]
