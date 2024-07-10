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


class ActivePaymentScheduleManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_paid=False)


class ActiveRentalManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(car__is_active=True)


class PaymentSchedule(models.Model):
    rental = models.ForeignKey('Rental', on_delete=models.CASCADE, related_name='payment_schedule')
    due_date = models.DateTimeField()
    payment_date = models.DateField()
    amount = models.DecimalField(max_digits=11, decimal_places=2)
    penalty_amount = models.DecimalField(max_digits=11, decimal_places=2, default=Decimal('0.0'))
    amount_paid = models.DecimalField(max_digits=11, decimal_places=2, default=Decimal('0.0'))
    paid_date = models.DateTimeField(null=True, blank=True)
    payment_closing_date = models.DateTimeField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)

    active_objects = ActivePaymentScheduleManager()
    objects = models.Manager()

    def __str__(self):
        return f"Payment of {self.amount} due on {self.due_date} for rental {self.rental}"

    class Meta:
        ordering = ['due_date']

    def calculate_payment(self):
        """
        To'lov miqdorini hisoblaydi, agar jarima qo'llanilishi kerak bo'lsa, uni ham hisoblaydi.
        """
        if self.is_paid:
            return self.amount

        # Jarimani hisoblash
        current_date = timezone.now()
        overdue_time = current_date - self.due_date
        penalty = Decimal('0.0')

        if self.rental.rent_type != 'credit' and overdue_time.total_seconds() > 0:
            penalty_rate = self.rental.penalty_percentage / Decimal('100.0')
            if self.rental.rent_type == 'monthly':
                overdue_days = overdue_time.days
                penalty = self.amount * penalty_rate * overdue_days
            elif self.rental.rent_type == 'daily':
                overdue_hours = overdue_time.total_seconds() // 3600
                penalty = self.amount * penalty_rate * overdue_hours

        total_payment = self.amount + penalty
        self.penalty_amount = penalty
        self.save()
        return total_payment

    def make_payment(self, payment_amount):
        """
        To'lovni amalga oshirish va tegishli maydonlarni yangilash.
        """
        total_payment = self.calculate_payment()

        self.amount_paid += payment_amount

        if self.amount_paid >= total_payment:
            self.is_paid = True
            self.paid_date = timezone.now()
            self.payment_closing_date = timezone.now()
        else:
            self.paid_date = timezone.now()

        self.save()

    def get_percentage_amount(self) -> Decimal:
        """
        To'lov jarimasini hisoblaydi
        """
        if self.is_paid:
            return Decimal('0.0')

        # Jarimani hisoblash
        current_date = timezone.now()
        overdue_time = current_date - self.due_date
        penalty = Decimal('0.0')

        if self.rental.rent_type != 'credit' and overdue_time.total_seconds() > 0:
            penalty_rate = self.rental.penalty_percentage / Decimal('100.0')
            if self.rental.rent_type == 'monthly':
                overdue_days = overdue_time.days
                penalty = self.amount * penalty_rate * overdue_days
            elif self.rental.rent_type == 'daily':
                overdue_hours = overdue_time.total_seconds() // 3600
                penalty = self.amount * penalty_rate * overdue_hours

        return Decimal(penalty)

    def get_total_amount(self) -> Decimal:
        """
        Umumiy to'lov summasi
        :return:
        """
        total_amount = self.amount + self.get_percentage_amount() - self.amount_paid
        return Decimal(total_amount)


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
    rent_amount = models.DecimalField(max_digits=11, decimal_places=2, validators=[MinValueValidator(Decimal('0.0'))])
    rent_period = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    initial_payment_amount = models.DecimalField(max_digits=11, decimal_places=2, default=Decimal('0.0'),
                                                 validators=[MinValueValidator(Decimal('0.0'))])
    penalty_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.0'),
                                             validators=[MinValueValidator(Decimal('0.0')),
                                                         MaxValueValidator(Decimal('100.0'))])
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=False, blank=True)
    closing_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    active_objects = ActiveRentalManager()

    def __str__(self):
        return f"{self.fullname}: {self.phone} ({self.car.__str__()})"

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

        if not PaymentSchedule.objects.filter(rental=self).exists():
            if self.rent_type == 'daily':
                self.create_payment_day_schedule()
            elif self.rent_type in ['monthly', 'credit']:
                self.create_payment_schedule()

    def create_payment_schedule(self):
        current_date = self.start_date
        for _ in range(self.rent_period):
            due_date = current_date + relativedelta(months=1)
            PaymentSchedule.objects.create(
                rental=self,
                due_date=due_date,
                payment_date=due_date.date(),
                amount=self.rent_amount
            )
            current_date = due_date

    def create_payment_day_schedule(self):
        PaymentSchedule.objects.create(
            rental=self,
            due_date=self.end_date,
            payment_date=self.end_date.date(),
            amount=self.rent_amount * self.rent_period
        )

    def get_total_amount(self):
        payment_schedules = PaymentSchedule.objects.filter(rental=self)
        total_amount = 0.0
        for payment_schedule in payment_schedules:
            total_amount += (payment_schedule.amount + payment_schedule.penalty_amount - payment_schedule.amount_paid)
        return total_amount
