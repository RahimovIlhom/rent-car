from django.contrib import admin

from .models import Rental, PaymentSchedule


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ['employee', 'fullname', 'car', 'rent_type', 'start_date', 'end_date', 'is_active']
    list_filter = ['employee']
    search_fields = ['employee', 'car']
    ordering = ['-start_date']


@admin.register(PaymentSchedule)
class PaymentScheduleAdmin(admin.ModelAdmin):
    list_display = ['rental', 'due_date', 'amount', 'penalty_amount', 'amount_paid', 'is_paid']
    list_filter = ['rental']
    search_fields = ['rental__fullname']
