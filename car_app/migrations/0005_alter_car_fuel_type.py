# Generated by Django 5.0.6 on 2024-07-09 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('car_app', '0004_alter_car_managers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='car',
            name='fuel_type',
            field=models.CharField(default='petrol', max_length=25),
        ),
    ]
