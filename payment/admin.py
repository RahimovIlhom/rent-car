from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['employee', 'rental', 'amount', 'created_at']
    list_filter = ['employee']
    search_fields = ['employee', 'rental', 'amount']
    ordering = ['-created_at']
