# Generated by Django 4.2.14 on 2024-07-10 19:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rent_app', '0009_alter_rental_penalty_percentage'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='rental',
            options={'ordering': ['-start_date']},
        ),
    ]
