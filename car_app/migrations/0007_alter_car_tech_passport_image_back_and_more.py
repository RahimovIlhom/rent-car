# Generated by Django 4.2.14 on 2024-07-12 05:28

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('car_app', '0006_alter_car_managers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='car',
            name='tech_passport_image_back',
            field=models.ImageField(blank=True, null=True, upload_to='cars/tech_passport/images', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpg', 'png', 'heic', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'])]),
        ),
        migrations.AlterField(
            model_name='car',
            name='tech_passport_image_front',
            field=models.ImageField(blank=True, null=True, upload_to='cars/tech_passport/images', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpg', 'png', 'heic', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'])]),
        ),
    ]