from dateutil.relativedelta import relativedelta
from django.db import transaction
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from datetime import date, timedelta
from rest_framework import generics, permissions, parsers
from rest_framework.views import APIView

from rent_app.models import PaymentSchedule, Rental
from rent_app.serializers import PaymentScheduleDashboardSerializer, PaymentScheduleListSerializer, \
    CreateRentalSerializer, ActiveRentalListSerializer, RentalRetrieveSerializer, NoActiveRentalListSerializer


# @method_decorator(csrf_exempt, name='dispatch')
# class PaymentScheduleDashboardView(generics.ListAPIView):
#     queryset = PaymentSchedule.objects.all()
#     serializer_class = PaymentScheduleDashboardSerializer
#     filter_backends = (filters.DjangoFilterBackend,)
#     filterset_class = PaymentScheduleFilter
#
#     def get_queryset(self):
#         queryset = PaymentSchedule.active_objects.all()
#         return queryset
#
#     @swagger_auto_schema(manual_parameters=[
#         openapi.Parameter(
#             'rent_type', openapi.IN_QUERY, description="Filter ijara turi bo'yicha",
#             type=openapi.TYPE_STRING, enum=['daily', 'monthly', 'credit'],
#         ),
#         openapi.Parameter(
#             'year', openapi.IN_QUERY, description="Filter yil bo'yicha",
#             type=openapi.TYPE_INTEGER
#         ),
#         openapi.Parameter(
#             'month', openapi.IN_QUERY, description="Filter oy bo'yicha",
#             type=openapi.TYPE_INTEGER
#         ),
#         openapi.Parameter(
#             'day', openapi.IN_QUERY, description="Filter kun bo'yicha",
#             type=openapi.TYPE_INTEGER
#         ),
#     ])
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)


@method_decorator(csrf_exempt, name='dispatch')
class PaymentScheduleDashboardView(generics.ListAPIView):
    serializer_class = PaymentScheduleDashboardSerializer

    def get_queryset(self):
        rent_type = self.request.query_params.get('rent_type', 'daily')
        today = timezone.localdate()

        if rent_type == 'daily':
            end_date = today + timedelta(days=3)
            return PaymentSchedule.active_objects.filter(
                payment_date__range=(today, end_date),
                rental__rent_type=rent_type
            )
        elif rent_type in ['monthly', 'credit']:
            start_date = today.replace(day=1)
            end_date = start_date + relativedelta(months=3)
            return PaymentSchedule.active_objects.filter(
                payment_date__range=(start_date, end_date),
                rental__rent_type=rent_type
            )
        else:
            return PaymentSchedule.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        rent_type = self.request.query_params.get('rent_type', 'daily')
        today = timezone.localdate()
        data = []

        if rent_type == 'daily':
            date_ranges = [today + timedelta(days=i) for i in range(3)]
            for d in date_ranges:
                filtered_schedules = queryset.filter(payment_date=d)
                data.append({
                    'date': d,
                    'payment_schedules': PaymentScheduleListSerializer(filtered_schedules, many=True).data
                })
        elif rent_type in ['monthly', 'credit']:
            start_date = today.replace(day=1)
            date_ranges = [start_date + relativedelta(months=i) for i in range(3)]
            for d in date_ranges:
                filtered_schedules = queryset.filter(payment_date__range=(d, d.replace(month=d.month + 1) - timedelta(days=1)))
                data.append({
                    'date': d,
                    'payment_schedules': PaymentScheduleListSerializer(filtered_schedules, many=True).data
                })

        return Response(data)

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter(
            'rent_type', openapi.IN_QUERY, description="Filter ijara turi bo'yicha",
            type=openapi.TYPE_STRING, enum=['daily', 'monthly', 'credit'],
        )
    ])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    class Meta:
        fields = ['date', 'payment_schedules']


@method_decorator(csrf_exempt, name='dispatch')
class ActiveRentalListAPIView(generics.ListAPIView):
    queryset = Rental.active_objects.all()
    serializer_class = ActiveRentalListSerializer
    permission_classes = [permissions.IsAuthenticated]


@method_decorator(csrf_exempt, name='dispatch')
class NoActiveRentalListAPIView(generics.ListAPIView):
    queryset = Rental.objects.all()
    serializer_class = NoActiveRentalListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(car__is_active=False)


@method_decorator(csrf_exempt, name='dispatch')
class RentalCreateAPIView(generics.CreateAPIView):
    queryset = Rental.active_objects.all()
    serializer_class = CreateRentalSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(data=serializer.data, status=201, headers=headers)


@method_decorator(csrf_exempt, name='dispatch')
class RentalRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Rental.objects.all()
    serializer_class = RentalRetrieveSerializer
    permission_classes = [permissions.IsAuthenticated]


@method_decorator(csrf_exempt, name='dispatch')
class SuccessfullyPaidAPIView(APIView):

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter(
            'payment_id', openapi.IN_QUERY, description="To'lov ID",
            type=openapi.TYPE_INTEGER
        )
    ])
    def post(self, request):
        payment_id = request.query_params.get('payment_id')
        try:
            payment = PaymentSchedule.active_objects.get(id=payment_id)
        except PaymentSchedule.DoesNotExist:
            return Response(data={'detail': 'To\'lov topilmadi'}, status=404)

        with transaction.atomic():
            payment.is_paid = True
            amount = payment.get_total_amount()
            payment.make_payment(amount)
            payment.save()

            rental = payment.rental
            payment_schedules = PaymentSchedule.active_objects.filter(rental=rental)
            if payment_schedules.count() == 0:
                rental.is_active = False
                rental.save()
                car = rental.car
                if rental.rent_type != 'credit':
                    car.status = 'active'
                    car.save()
                else:
                    car.status = 'sold'
                    car.is_active = False
                    car.save()

        return Response(data={'message': 'To\'lov muvaffaqiyatli amalga oshirildi'}, status=200)
