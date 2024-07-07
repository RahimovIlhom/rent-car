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

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.fullname}: {self.phone} ({self.car.__str__()})"

    def total_rental_amount(self):
        return self.rent_amount * self.rent_period

    def penalty_amount_of_daily_rent(self):
        if self.rent_type == 'daily':
            if self.closing_date:
                time_difference = self.closing_date - self.end_date
                delayed_hours = time_difference.total_seconds() // 3600
                hourly_penalty = self.rent_amount * self.penalty_percentage / 100
                return hourly_penalty * delayed_hours
            else:
                return 0
        else:
            return 0

    def this_month_paid_amount(self):
        payments = self.payments.filter(created_at__year=timezone.now().year, created_at__month=timezone.now().month)
        total = sum(map(lambda p: p.amount, payments))
        return total

    def this_month_penalty_amount(self):
        interval_months_count = timezone.now().month - self.start_date.month
        this_month_payment_date = self.start_date + relativedelta(months=interval_months_count)
        if this_month_payment_date > timezone.now():
            return 0
        delayed_days = (timezone.now() - this_month_payment_date).days
        daily_penalty = self.rent_amount * self.penalty_percentage / 100
        penalty_amount = daily_penalty * delayed_days
        return penalty_amount

    def this_month_debt_amount(self):
        this_month_paid = self.this_month_paid_amount()
        this_month_penalty = self.this_month_penalty_amount()
        if self.rent_type == 'monthly':
            total = self.rent_amount - this_month_paid + this_month_penalty
        else:
            total = self.rent_amount - this_month_paid
        return total

    def total_price(self):
        if self.rent_type == 'daily':
            return self.total_rental_amount() + self.penalty_amount_of_daily_rent()
        elif self.rent_type == 'monthly':
            return self.total_rental_amount() + self.this_month_penalty_amount()
        else:
            return self.total_rental_amount()

    def total_paid_amount(self):
        payments = self.payments.all()
        total = sum(map(lambda p: p.amount, payments))
        return total + self.initial_payment_amount

    def total_penalty_amount(self):
        payments = self.payments.all()
        total = sum(map(lambda p: p.penalty_amount, payments))
        return total

    def total_debt_amount(self):
        return self.total_price() - (self.total_paid_amount() - self.total_penalty_amount())
