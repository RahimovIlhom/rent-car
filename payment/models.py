from django.contrib.auth import get_user_model
from django.db import models

from rent_app.models import Rental


employee_model = get_user_model()


class Payment(models.Model):
    employee = models.ForeignKey(employee_model, on_delete=models.CASCADE, related_name='payments')
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    penalty_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.amount} {self.created_at}"

    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
