from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from users.serializers import EmployeeSerializer
from .models import Car


class DashboardCarSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Car
        fields = ['id', 'name', 'status']


CAR_STATUS = (
    ('active', 'Active'),
    ('unrepaired', 'Unrepaired'),
)


class CarCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    employee = EmployeeSerializer(read_only=True)
    car_year = serializers.IntegerField(required=True, validators=[MinValueValidator(1990), MaxValueValidator(2100)])
    status = serializers.ChoiceField(required=False, choices=CAR_STATUS, default='active')
    tech_passport_image_front = serializers.ImageField(required=False)
    tech_passport_image_back = serializers.ImageField(required=False)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Car
        fields = ['id', 'employee', 'name', 'car_number', 'car_year', 'information', 'tech_passport_number',
                  'tech_passport_image_front', 'tech_passport_image_back', 'fuel_type', 'status',
                  'created_at', 'updated_at']
        extra_kwargs = {
            'employee': {'write_only': True},
        }


class CarListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    employee = EmployeeSerializer(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Car
        fields = ['id', 'employee', 'name', 'car_number', 'car_year', 'information', 'tech_passport_number',
                  'fuel_type', 'status', 'created_at', 'updated_at']
        extra_kwargs = {
            'employee': {'write_only': True},
        }


class CarDetailSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    employee = EmployeeSerializer(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Car
        fields = ['id', 'employee', 'name', 'car_number', 'car_year', 'information', 'tech_passport_number',
                  'tech_passport_image_front', 'tech_passport_image_back', 'fuel_type', 'status',
                  'created_at', 'updated_at']
        extra_kwargs = {
            'employee': {'write_only': True},
        }


class CarUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    employee = EmployeeSerializer(read_only=True)
    name = serializers.CharField(max_length=255, required=False)
    car_number = serializers.CharField(max_length=255, required=False)
    tech_passport_number = serializers.CharField(max_length=255, required=False)
    status = serializers.ChoiceField(required=False, choices=CAR_STATUS, default='active')
    car_year = serializers.IntegerField(required=False, validators=[MinValueValidator(1990), MaxValueValidator(2100)])
    tech_passport_image_front = serializers.ImageField(required=False)
    tech_passport_image_back = serializers.ImageField(required=False)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Car
        fields = ['id', 'employee', 'name', 'car_number', 'car_year', 'information', 'tech_passport_number',
                  'tech_passport_image_front', 'tech_passport_image_back', 'fuel_type', 'status',
                  'created_at', 'updated_at']
        extra_kwargs = {
            'employee': {'write_only': True},
        }

    def update(self, instance, validated_data):
        if instance.status not in ['active', 'unrepaired']:
            return ValidationError({'status': 'Mashinaning holati faol yoki ta\'mirlanmagan bo\'lgan holatda '
                                              'o\'zgartirish mumkin'})
        instance.name = validated_data.get('name', instance.name)
        instance.car_number = validated_data.get('car_number', instance.car_number)
        instance.car_year = validated_data.get('car_year', instance.car_year)
        instance.information = validated_data.get('information', instance.information)
        instance.tech_passport_number = validated_data.get('tech_passport_number', instance.tech_passport_number)
        instance.tech_passport_image_front = validated_data.get('tech_passport_image_front',
                                                                instance.tech_passport_image_front)
        instance.tech_passport_image_back = validated_data.get('tech_passport_image_back',
                                                               instance.tech_passport_image_back)
        instance.fuel_type = validated_data.get('fuel_type', instance.fuel_type)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance
