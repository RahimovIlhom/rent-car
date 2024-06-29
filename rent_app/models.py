from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from car_app.models import Car

employee_model = get_user_model()

RENT_TYPES = (
    ('daily', 'Daily'),
    ('monthly', 'Monthly'),
    ('credit', 'Credit'),
)


class Rental(models.Model):
    employee = models.ForeignKey(employee_model, on_delete=models.CASCADE, related_name='rentals')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='rentals')
    fullname = models.CharField(max_length=255)
    phone = models.CharField(max_length=50)
    passport = models.CharField(max_length=50)
    passport_image_front = models.ImageField(upload_to='rentals/passport/images', null=True, blank=True)
    passport_image_back = models.ImageField(upload_to='rentals/passport/images', null=True, blank=True)
    rent_type = models.CharField(max_length=20, choices=RENT_TYPES, default='daily')
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.0)])
    rent_period = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    initial_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0,
                                         validators=[MinValueValidator(0.0)])
    penalty_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0,
                                             validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=False, blank=True)
    closing_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'rentals'
        ordering = ['-start_date']

    def save(self, *args, **kwargs):
        if not self.pk:
            self.start_date = timezone.now()
        if self.rent_type == 'daily':
            rent_hour = self.start_date.hour
            self.end_date = self.start_date + timedelta(days=self.rent_period)
            self.end_date = self.end_date.replace(hour=rent_hour + 1, minute=0, second=0, microsecond=0)
        elif self.rent_type in ['monthly', 'credit']:
            self.end_date = self.start_date + relativedelta(months=self.rent_period)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.fullname}: {self.phone} ({self.car.__str__()})"

    # def total_rental_amount(self):
    #     if self.rent_type == 'daily':
    #         time_difference = self.end_date - self.start_date
    #         all_days = time_difference.days
    #         return self.rent_amount * all_days
    #     elif self.rent_type == 'monthly':
    #         time_difference = self.end_date - self.start_date
    #         all_months = time_difference.days / 30
    #         return self.rent_amount * all_months
    #     elif self.rent_type == 'credit':
    #         time_difference = self.end_date - self.start_date
    #         all_months = time_difference.days // 30
    #         return self.rent_amount * all_months
    #     else:
    #         return 0
    #
    # def penalty_amount(self):
    #     if self.rent_type == 'daily':
    #         if self.closing_date:
    #             time_difference = self.closing_date - self.end_date
    #             delayed_hours = time_difference.total_seconds() // 3600
    #             hourly_penalty = self.rent_amount * self.penalty_percentage / 100
    #             return hourly_penalty * delayed_hours
    #         else:
    #             return 0
    #     elif self.rent_type == 'monthly':
    #         if self.closing_date:
    #             time_difference = self.closing_date - self.end_date
    #             delayed_days = time_difference.days
    #             daily_penalty = self.rent_amount * self.penalty_percentage / 100
    #             return delayed_days * daily_penalty
    #         else:
    #             return 0
    #     else:
    #         return 0
    #
    # def total_price(self):
    #     return self.total_rental_amount() + self.penalty_amount()
    #
    # def total_paid_amount(self):
    #     payments = self.payments.all()
    #     total = sum(map(lambda p: p.amount, payments))
    #     return total + self.initial_amount
    #
    # def total_debt_amount(self):
    #     return self.total_price() - self.total_paid_amount()
