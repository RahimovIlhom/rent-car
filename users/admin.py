from django.contrib import admin

from .models import Employee


@admin.register(Employee)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'fullname', 'phone')
    list_filter = ('username', 'fullname', 'phone')
    search_fields = ('username', 'fullname', 'phone')

    def fullname(self, obj):
        return obj.fullname

    def phone(self, obj):
        return obj.phone

    fullname.short_description = 'Ism-familiya'
    phone.short_description = 'Telefon raqam'
