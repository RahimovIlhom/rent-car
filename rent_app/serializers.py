from decimal import Decimal

from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework import serializers

from car_app.models import Car
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


class CreateRentalSerializer(serializers.ModelSerializer):
    car_id = serializers.IntegerField(write_only=True)
    RENT_TYPE_CHOICES = [
        ('daily', 'Daily'),
        ('monthly', 'Monthly'),
        ('credit', 'Credit'),
    ]
    rent_type = serializers.ChoiceField(choices=RENT_TYPE_CHOICES)
    rent_amount = serializers.DecimalField(max_digits=11, decimal_places=2, required=True,
                                           validators=[MinValueValidator(Decimal('0.0'))])
    rent_period = serializers.IntegerField(validators=[MinValueValidator(1)])
    initial_payment_amount = serializers.DecimalField(max_digits=11, decimal_places=2, default=Decimal('0.0'),
                                                      validators=[MinValueValidator(Decimal('0.0'))])
    penalty_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.0'),
                                                  validators=[MinValueValidator(Decimal('0.0')),
                                                              MaxValueValidator(Decimal('100.0'))])
    passport_image_front = serializers.ImageField(required=False, allow_null=True)
    passport_image_back = serializers.ImageField(required=False, allow_null=True)
    receipt_image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Rental
        fields = ['car_id', 'fullname', 'phone', 'passport', 'passport_image_front', 'passport_image_back',
                  'receipt_image', 'rent_type', 'rent_amount', 'rent_period', 'initial_payment_amount',
                  'penalty_percentage']

    def create(self, validated_data):
        car_id = validated_data.pop('car_id')
        try:
            car = Car.objects.get(id=car_id)
        except Car.DoesNotExist:
            raise serializers.ValidationError({'car_id': 'Mashina topilmadi'})
        user = self.context['request'].user
        validated_data['employee'] = user
        validated_data['car'] = car
        return super().create(validated_data)
