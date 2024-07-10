from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework.response import Response

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'fullname', 'phone', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super(UserSerializer, self).create(validated_data)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'fullname', 'phone')


class EmployeesListSerializer(serializers.ModelSerializer):
    is_admin = serializers.SerializerMethodField('get_is_admin')

    class Meta:
        model = User
        fields = ('id', 'username', 'fullname', 'phone', 'is_admin')

    def get_is_admin(self, obj):
        return obj.is_staff


class EmployeeUpdateSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ('user_id', 'username', 'fullname', 'phone')

    def update(self, instance, validated_data):
        user_id = validated_data.get('user_id')
        try:
            instance = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(data={'detail': 'Foydalanuvchi topilmadi!'}, status=404)
        instance.username = validated_data.get('username', instance.username)
        instance.fullname = validated_data.get('fullname', instance.fullname)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.save()
        return instance
