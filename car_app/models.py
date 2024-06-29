from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


employee = get_user_model()

FUEL_TYPES = (
    ('petrol', 'Petrol'),
    ('electric', 'Electric'),
    ('petrol_gas', 'Petrol Gas'),
    ('methane_gas', 'Methane Gas'),
    ('propane_gas', 'Propane Gas'),
    ('diesel', 'Diesel'),
    ('other', 'Other'),
)

CAR_STATUS = (
    ('active', 'Active'),
    ('rented', 'Rented'),
    ('unrepaired', 'Unrepaired'),
    ('sold', 'Sold'),
)


class Car(models.Model):
    name = models.CharField(max_length=255)
    car_number = models.CharField(max_length=255)
    car_year = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1800),
                                                                              MaxValueValidator(2100)])
    information = models.TextField(null=True, blank=True)
    tech_passport_number = models.CharField(max_length=255)
    tech_passport_image_front = models.ImageField(upload_to='cars/tech_passport/images', null=True, blank=True)
    tech_passport_image_back = models.ImageField(upload_to='cars/tech_passport/images', null=True, blank=True)
    fuel_type = models.CharField(max_length=25, choices=FUEL_TYPES, default='petrol')
    status = models.CharField(max_length=25, choices=CAR_STATUS, default='active')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.car_number})"

    class Meta:
        db_table = 'cars'


class CarImage(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='cars/images')

    class Meta:
        db_table = 'car_images'

    def __str__(self):
        return f"{self.car.name} ({self.car.car_number})"
