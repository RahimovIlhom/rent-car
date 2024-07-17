from decimal import Decimal

from django.core.validators import MinValueValidator
from rest_framework import serializers

from rent_app.models import Rental
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
