from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('employee', 'rental', 'amount', 'created_at')
    ordering = ['-created_at']
