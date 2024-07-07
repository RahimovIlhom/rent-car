from rest_framework import serializers

from car_app.serializers import DashboardCarSerializer
from .models import Rental


class RentalDashboardSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    debt_amount = serializers.SerializerMethodField()
    car = DashboardCarSerializer(read_only=True)

    class Meta:
        model = Rental
        fields = ['id', 'car', 'fullname', 'phone', 'rent_type', 'rent_amount', 'debt_amount', 'start_date', 'end_date']

    def get_debt_amount(self, obj):
        if obj.rent_type == 'daily':
            return obj.total_debt_amount()
        else:
            return obj.this_month_debt_amount()
