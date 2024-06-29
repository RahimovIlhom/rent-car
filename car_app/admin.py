from django.contrib import admin

from .models import Car, CarImage


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('name', 'car_number', 'car_year', 'fuel_type', 'status', 'is_active')
    list_filter = ('fuel_type', 'status', 'is_active')
    search_fields = ('name', 'car_number', 'car_year', 'fuel_type', 'status', 'is_active')


@admin.register(CarImage)
class CarImageAdmin(admin.ModelAdmin):
    list_display = ('car', 'image')
    list_filter = ('car', )
    search_fields = ('car', 'image')
