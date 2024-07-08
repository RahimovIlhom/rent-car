from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from car_app.models import Car
from car_app.serializers import CarCreateSerializer, CarListSerializer, CarDetailSerializer, CarUpdateSerializer


@method_decorator(csrf_exempt, name='dispatch')
class CarCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CarCreateSerializer

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the car'),
                'car_number': openapi.Schema(type=openapi.TYPE_STRING, description='Car number'),
                'car_year': openapi.Schema(type=openapi.TYPE_INTEGER, description='Car year'),
                'information': openapi.Schema(type=openapi.TYPE_STRING, description='Information about the car'),
                'tech_passport_number': openapi.Schema(type=openapi.TYPE_STRING, description='Tech passport number'),
                'fuel_type': openapi.Schema(type=openapi.TYPE_STRING, description='Fuel type',
                                            enum=['petrol', 'electric', 'petrol_gas', 'methane_gas', 'propane_gas', 'diesel', 'other']),
                'status': openapi.Schema(type=openapi.TYPE_STRING, description='Status of the car',
                                         enum=['active', 'unrepaired']),
                'tech_passport_image_front': openapi.Schema(type=openapi.TYPE_FILE,
                                                            description='Front image of tech passport'),
                'tech_passport_image_back': openapi.Schema(type=openapi.TYPE_FILE,
                                                           description='Back image of tech passport'),
            },
            required=['name', 'car_number', 'car_year', 'tech_passport_number', 'fuel_type']
        ),
        responses={201: CarCreateSerializer, 400: 'Bad Request'}
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data['status'] in ['active', 'unrepaired']:
            serializer.save(employee=request.user)  # request.user ni employee maydoniga saqlaymiz
            return Response(data=serializer.data, status=201)
        else:
            return Response(data={'detail': 'Invalid status'}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class CarDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CarDetailSerializer

    @swagger_auto_schema(
        responses={
            200: CarDetailSerializer,
            404: openapi.Response(
                description="Mashina topilmadi",
                examples={
                    "application/json": {
                        "detail": "Mashina topilmadi"
                    }
                }
            )
        }
    )
    def get(self, request, car_id):
        try:
            car = Car.active_objects.get(id=car_id)
        except Car.DoesNotExist:
            return Response(data={'message': 'Mashina topilmadi'}, status=404)
        serializer = self.serializer_class(car)
        return Response(data=serializer.data)


@method_decorator(csrf_exempt, name='dispatch')
class UnRepairedCarsListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CarListSerializer

    @swagger_auto_schema(
        responses={200: CarListSerializer(many=True)}
    )
    def get(self, request):
        cars = Car.active_objects.filter(status='unrepaired')
        serializer = self.serializer_class(cars, many=True)
        return Response(data=serializer.data)


@method_decorator(csrf_exempt, name='dispatch')
class ActivateCarAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'car_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Car id')
            },
            required=['car_id']
        ),
        responses={
            200: openapi.Response(
                description="Avtomobilni faollashtirish",
                examples={
                    "application/json": {
                        "detail": "Avtomobil muvaffaqiyatli faollashtirildi"
                    }
                }
            ),
            400: openapi.Response(
                description="Avtomobil allaqachon faollashtirilgan",
                examples={
                    "application/json": {
                        "error": "Avtomobil allaqachon faollashtirilgan"
                    }
                }
            ),
            404: openapi.Response(
                description="Avtomobil topilmasa",
                examples={
                    "application/json": {
                        "detail": "Avtomobil topilmadi"
                    }
                }
            ),
        }
    )
    def post(self, request):
        car_id = request.data.get('car_id')
        try:
            car = Car.active_objects.get(id=car_id)
        except Car.DoesNotExist:
            return Response(data={'detail': 'Avtomobil topilmadi'}, status=404)
        if car.status == 'active':
            return Response(data={'error': 'Avtomobil allaqachon faollashtirilgan'}, status=400)
        car.status = 'active'
        car.save()
        return Response(data={'detail': 'Avtomobil muvaffaqiyatli faollashtirildi'}, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class DeActivateCarAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'car_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Car id')
            },
            required=['car_id']
        ),
        responses={
            200: openapi.Response(
                description="Avtomobilni faolsizlantirish",
                examples={
                    "application/json": {
                        "detail": "Avtomobil faolsizlantirildi"
                    }
                }
            ),
            400: openapi.Response(
                description="Avtomobil allaqachon faolsizlantirilgan",
                examples={
                    "application/json": {
                        "error": "Avtomobil allaqachon faolsizlantirilgan"
                    }
                }
            ),
            404: openapi.Response(
                description="Avtomobil topilmasa",
                examples={
                    "application/json": {
                        "detail": "Avtomobil topilmadi"
                    }
                }
            ),
        }
    )
    def post(self, request):
        car_id = request.data.get('car_id')
        try:
            car = Car.active_objects.get(id=car_id)
        except Car.DoesNotExist:
            return Response(data={'detail': 'Avtomobil topilmadi'}, status=404)
        if car.status == 'unrepaired':
            return Response(data={'error': 'Avtomobil allaqachon faolsizlantirilgan'}, status=400)
        car.status = 'unrepaired'
        car.save()
        return Response(data={'detail': 'Avtomobil muvaffaqiyatli faolsizlantirildi'}, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class CarListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CarListSerializer

    @swagger_auto_schema(
        responses={200: CarListSerializer(many=True)}
    )
    def get(self, request):
        cars = Car.active_objects.all()
        serializer = self.serializer_class(cars, many=True)
        return Response(data=serializer.data)


@method_decorator(csrf_exempt, name='dispatch')
class ActiveCarListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CarListSerializer

    @swagger_auto_schema(
        responses={200: CarListSerializer(many=True)}
    )
    def get(self, request):
        cars = Car.active_objects.filter(status='active')
        serializer = self.serializer_class(cars, many=True)
        return Response(data=serializer.data)


@method_decorator(csrf_exempt, name='dispatch')
class CarUpdateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CarUpdateSerializer

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the car'),
                'car_number': openapi.Schema(type=openapi.TYPE_STRING, description='Car number'),
                'car_year': openapi.Schema(type=openapi.TYPE_INTEGER, description='Car year'),
                'information': openapi.Schema(type=openapi.TYPE_STRING, description='Information about the car'),
                'tech_passport_number': openapi.Schema(type=openapi.TYPE_STRING, description='Tech passport number'),
                'fuel_type': openapi.Schema(type=openapi.TYPE_STRING, description='Fuel type',
                                            enum=['petrol', 'electric', 'petrol_gas', 'methane_gas', 'propane_gas',
                                                  'diesel', 'other']),
                'status': openapi.Schema(type=openapi.TYPE_STRING, description='Status of the car',
                                         enum=['active', 'unrepaired']),
                'tech_passport_image_front': openapi.Schema(type=openapi.TYPE_FILE,
                                                            description='Front image of tech passport'),
                'tech_passport_image_back': openapi.Schema(type=openapi.TYPE_FILE,
                                                           description='Back image of tech passport'),
            },
            required=[]
        ),
        responses={
            200: CarUpdateSerializer,
            404: openapi.Response(
                description="Avtomobil topilmadi",
                examples={
                    "application/json": {
                        "detail": "Avtomobil topilmadi"
                    }
                }
            )
        }
    )
    def patch(self, request, car_id):
        try:
            car = Car.active_objects.get(id=car_id)
        except Car.DoesNotExist:
            return Response(data={'detail': 'Avtomobil topilmadi'}, status=404)
        serializer = self.serializer_class(data=request.data, instance=car)
        serializer.is_valid(raise_exception=True)
        serializer.employee = request.user
        serializer.save()
        return Response(data=serializer.data, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class CarDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        responses={
            204: openapi.Response(
                description="Avtomobil o`chirildi",
            ),
            404: openapi.Response(
                description="Avtomobil topilmadi",
                examples={
                    "application/json": {
                        "detail": "Avtomobil topilmadi"
                    }
                }
            )
        }
    )
    def delete(self, request, car_id):
        try:
            car = Car.active_objects.get(id=car_id)
        except Car.DoesNotExist:
            return Response(data={'detail': 'Avtomobil topilmadi'}, status=404)
        if car.status == 'rented':
            return Response(data={'error': 'Avtomobilni o\'chira olmaysiz!'}, status=400)
        car.is_active = False
        car.save()

        return Response(status=204)
