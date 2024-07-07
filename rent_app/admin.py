from django.contrib import admin

from .models import Rental


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ['employee', 'fullname', 'car', 'rent_type', 'start_date', 'end_date']
    list_filter = ['employee']
    search_fields = ['employee', 'car']
    ordering = ['-start_date']
