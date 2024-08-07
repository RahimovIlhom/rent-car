from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

from rent_app.models import PaymentSchedule, Rental


employee_model = get_user_model()


class Payment(models.Model):
    employee = models.ForeignKey(employee_model, on_delete=models.CASCADE)
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=11, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment of {self.amount} due on {self.created_at}"

    def save(self, *args, **kwargs):
        if not self.pk:
            excess_amount = self.amount
            while excess_amount > 0.0:
                payment_schedule = PaymentSchedule.active_objects.filter(rental=self.rental).first()
                if payment_schedule:
                    excess_amount = payment_schedule.make_payment(excess_amount)
                else:
                    excess_amount = Decimal('0.0')
        payment_schedules = PaymentSchedule.active_objects.filter(rental=self.rental)
        if payment_schedules.count() == 0:
            self.rental.is_active = False
            self.rental.closing_date = timezone.now().date()
            self.rental.save()
            car = self.rental.car
            if self.rental.rent_type != 'credit':
                car.status = 'active'
                car.save()
            else:
                car.status = 'sold'
                car.is_active = False
                car.save()
        super().save(*args, **kwargs)
