from decimal import Decimal

from django.core.validators import MinValueValidator
from rest_framework import serializers

from rent_app.models import Rental
from rent_app.serializers import RentalDashboardSerializer
from users.serializers import EmployeeSerializer
from .models import Payment


class PaymentCreateSerializer(serializers.ModelSerializer):
    rental_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=11, decimal_places=2, validators=[MinValueValidator(Decimal('0.0'))])

    class Meta:
        model = Payment
        fields = ['rental_id', 'amount']

    def create(self, validated_data):
        rental_id = validated_data.pop('rental_id')
        try:
            rental = Rental.active_objects.get(pk=rental_id)
        except Rental.DoesNotExist:
            raise serializers.ValidationError('Ijara shartnoma topilmadi')
        employee = self.context['request'].user
        return Payment.objects.create(rental=rental, employee=employee, **validated_data)


class RentalPaymentsListSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    rental = RentalDashboardSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'employee', 'rental', 'amount', 'created_at']


class PaymentsListSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'employee', 'rental', 'amount', 'created_at']
