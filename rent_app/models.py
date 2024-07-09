from datetime import timedelta
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from rest_framework.exceptions import ValidationError

from car_app.models import Car

employee_model = get_user_model()

RENT_TYPES = (
    ('daily', 'Daily'),
    ('monthly', 'Monthly'),
    ('credit', 'Credit'),
)


class ActiveRentalManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(car__is_active=True)


class PaymentSchedule(models.Model):
    rental = models.ForeignKey('Rental', on_delete=models.CASCADE, related_name='payment_schedule')
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Payment of {self.amount} due on {self.due_date} for rental {self.rental}"


class Rental(models.Model):
    employee = models.ForeignKey(employee_model, on_delete=models.CASCADE, related_name='rentals')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='rentals')
    fullname = models.CharField(max_length=255)
    phone = models.CharField(max_length=50)
    passport = models.CharField(max_length=50)
    passport_image_front = models.ImageField(upload_to='rentals/passport/images', null=True, blank=True)
    passport_image_back = models.ImageField(upload_to='rentals/passport/images', null=True, blank=True)
    receipt_image = models.ImageField(upload_to='rentals/receipt/images', null=True, blank=True)
    rent_type = models.CharField(max_length=20, choices=RENT_TYPES, default='daily')
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.0'))])
    rent_period = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    initial_payment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.0'),
                                                 validators=[MinValueValidator(Decimal('0.0'))])
    penalty_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.0'),
                                             validators=[MinValueValidator(Decimal('0.0')), MaxValueValidator(Decimal('100.0'))])
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=False, blank=True)
    closing_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    active_objects = ActiveRentalManager()

    class Meta:
        db_table = 'rentals'
        ordering = ['end_date']

    def save(self, *args, **kwargs):
        if not self.pk:
            self.start_date = timezone.now()
            if self.car.status == 'active':
                self.car.status = 'rented'
                self.car.save()
            else:
                raise ValidationError(detail="This car is not active for rent.", code=400)

            if self.rent_type == 'daily':
                rent_hour = self.start_date.hour
                self.end_date = self.start_date + timedelta(days=self.rent_period)
                self.end_date = self.end_date.replace(hour=rent_hour + 1, minute=0, second=0, microsecond=0)
            elif self.rent_type in ['monthly', 'credit']:
                self.end_date = self.start_date + relativedelta(months=self.rent_period)
                self.create_payment_schedule()

        super().save(*args, **kwargs)

    def create_payment_schedule(self):
        current_date = self.start_date
        for _ in range(self.rent_period):
            due_date = current_date + relativedelta(months=1)
            PaymentSchedule.objects.create(
                rental=self,
                due_date=due_date,
                amount=self.rent_amount
            )
            current_date = due_date

    def __str__(self):
        return f"{self.fullname}: {self.phone} ({self.car.__str__()})"
