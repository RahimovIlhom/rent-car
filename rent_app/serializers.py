from decimal import Decimal

from rest_framework import serializers

from car_app.serializers import DashboardCarSerializer
from .models import Rental, PaymentSchedule


class RentalDashboardSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    car = DashboardCarSerializer(read_only=True)

    class Meta:
        model = Rental
        fields = ['id', 'fullname', 'phone', 'car']


class PaymentScheduleListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    rental = RentalDashboardSerializer(read_only=True)
    total_amount = serializers.SerializerMethodField('get_total_amount')
    percentage_amount = serializers.SerializerMethodField('get_percentage_amount')
    rent_type = serializers.SerializerMethodField('get_rent_type')

    class Meta:
        model = PaymentSchedule
        fields = ['id', 'rental', 'amount', 'total_amount', 'percentage_amount', 'amount_paid', 'rent_type',
                  'due_date', 'is_paid']

    def get_total_amount(self, obj) -> Decimal:
        return obj.get_total_amount()

    def get_percentage_amount(self, obj) -> Decimal:
        return obj.get_percentage_amount()

    def get_rent_type(self, obj):
        return obj.rental.rent_type


class PaymentScheduleDashboardSerializer(serializers.Serializer):
    date = serializers.DateField()
    payment_schedules = PaymentScheduleListSerializer(many=True)

    class Meta:
        fields = ['date', 'payment_schedules']


class ActiveRentalListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    car = DashboardCarSerializer(read_only=True)
    total_amount = serializers.SerializerMethodField('get_total_amount')

    class Meta:
        model = Rental
        fields = ['id', 'fullname', 'phone', 'start_date', 'end_date', 'rent_type', 'status', 'total_amount', 'car']

    def get_total_amount(self, obj) -> Decimal:
        return obj.get_total_amount()
