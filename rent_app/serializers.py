from decimal import Decimal

from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework import serializers

from car_app.models import Car
from car_app.serializers import DashboardCarSerializer, CarDetailSerializer
from users.serializers import EmployeeSerializer
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
    currency = serializers.SerializerMethodField('get_currency')

    class Meta:
        model = PaymentSchedule
        fields = ['id', 'rental', 'currency', 'amount', 'total_amount', 'percentage_amount', 'amount_paid', 'rent_type',
                  'due_date', 'is_paid']

    def get_total_amount(self, obj) -> Decimal:
        return obj.get_total_amount()

    def get_percentage_amount(self, obj) -> Decimal:
        return obj.get_percentage_amount()

    def get_rent_type(self, obj):
        return obj.rental.rent_type

    def get_currency(self, obj):
        return obj.rental.currency


class PaymentScheduleDashboardSerializer(serializers.Serializer):
    date = serializers.DateField()
    payment_schedules = PaymentScheduleListSerializer(many=True)

    class Meta:
        fields = ['date', 'payment_schedules']


class ActiveRentalListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    car = DashboardCarSerializer(read_only=True)
    total_amount = serializers.SerializerMethodField('get_total_amount')
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = Rental
        fields = ['id', 'employee', 'fullname', 'phone', 'start_date', 'end_date', 'rent_type', 'currency',
                  'total_amount', 'car']

    def get_total_amount(self, obj) -> Decimal:
        return obj.get_total_amount()


class NoActiveRentalListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    car = DashboardCarSerializer(read_only=True)
    total_paid_amount = serializers.SerializerMethodField('get_total_paid_amount')
    employee = EmployeeSerializer(read_only=True)
    block_rental = serializers.SerializerMethodField('get_block_rental')

    class Meta:
        model = Rental
        fields = ['id', 'employee', 'fullname', 'phone', 'start_date', 'end_date', 'closing_date', 'rent_type',
                  'currency', 'total_paid_amount', 'car', 'block_rental']

    def get_total_paid_amount(self, obj) -> Decimal:
        return obj.get_total_paid_amount()

    def get_block_rental(self, obj) -> bool:
        return obj.bad_rental


class CreateRentalSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
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
    payment_date = serializers.DateField(required=False)
    initial_payment_amount = serializers.DecimalField(max_digits=11, decimal_places=2, default=Decimal('0.0'),
                                                      validators=[MinValueValidator(Decimal('0.0'))])
    penalty_amount = serializers.DecimalField(max_digits=11, decimal_places=2, default=Decimal('0.0'),
                                              validators=[MinValueValidator(Decimal('0.0'))])
    passport_image_front = serializers.ImageField(required=False, allow_null=True)
    passport_image_back = serializers.ImageField(required=False, allow_null=True)
    receipt_image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Rental
        fields = ['id', 'car_id', 'fullname', 'phone', 'passport', 'passport_image_front', 'passport_image_back',
                  'receipt_image', 'rent_type', 'currency', 'rent_amount', 'rent_period', 'payment_date',
                  'initial_payment_amount', 'penalty_amount']

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


class PaymentScheduleListForRentalSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    penalty_amount = serializers.SerializerMethodField('get_penalty_amount')
    total_amount = serializers.SerializerMethodField('get_total_amount')

    class Meta:
        model = PaymentSchedule
        fields = ['id', 'due_date', 'amount', 'penalty_amount', 'total_amount', 'amount_paid', 'payment_closing_date',
                  'is_paid']

    def get_penalty_amount(self, obj) -> Decimal:
        return obj.get_percentage_amount()

    def get_total_amount(self, obj) -> Decimal:
        return obj.get_total_amount()


class RentalRetrieveSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    car = CarDetailSerializer(read_only=True)
    payment_schedules = serializers.SerializerMethodField('get_payment_schedules')
    amount = serializers.SerializerMethodField('get_amount')
    total_amount = serializers.SerializerMethodField('get_total_amount')
    total_penalty_amount = serializers.SerializerMethodField('get_total_penalty_amount')
    total_paid_amount = serializers.SerializerMethodField('get_paid_amount')

    class Meta:
        model = Rental
        fields = ['id', 'employee', 'car', 'fullname', 'phone', 'passport', 'passport_image_front',
                  'passport_image_back', 'receipt_image', 'rent_type', 'rent_amount', 'rent_period',
                  'initial_payment_amount', 'penalty_amount', 'start_date', 'end_date', 'closing_date',
                  'is_active', 'payment_schedules', 'currency', 'amount', 'total_amount', 'total_penalty_amount',
                  'total_paid_amount']

    def get_payment_schedules(self, obj):
        return PaymentScheduleListForRentalSerializer(obj.payment_schedule.all(), many=True).data

    def get_amount(self, obj) -> Decimal:
        return obj.get_amount()

    def get_total_amount(self, obj) -> Decimal:
        return obj.get_total_amount()

    def get_total_penalty_amount(self, obj) -> Decimal:
        payment_schodules = obj.payment_schedule.all()
        total_penalty_amount = Decimal('0.0')
        for payment_schedule in payment_schodules:
            total_penalty_amount += payment_schedule.penalty_amount
        return total_penalty_amount

    def get_paid_amount(self, obj) -> Decimal:
        return obj.get_total_paid_amount()
