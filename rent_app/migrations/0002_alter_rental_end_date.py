# Generated by Django 5.0.6 on 2024-06-29 11:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rent_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rental',
            name='end_date',
            field=models.DateTimeField(blank=True),
        ),
    ]
