from decimal import Decimal

from dateutil.relativedelta import relativedelta
from django.db import transaction
from django.http import HttpResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from datetime import date, timedelta
from rest_framework import generics, permissions, parsers
from rest_framework.views import APIView

from car_app.models import Car
from rent_app.models import PaymentSchedule, Rental
from rent_app.serializers import PaymentScheduleDashboardSerializer, PaymentScheduleListSerializer, \
    CreateRentalSerializer, ActiveRentalListSerializer, RentalRetrieveSerializer, NoActiveRentalListSerializer
from rent_app.utils import pdf_writer


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

        if rent_type == 'daily':
            return PaymentSchedule.active_objects.filter(
                rental__rent_type=rent_type
            )
        elif rent_type in ['monthly', 'credit']:
            return PaymentSchedule.active_objects.filter(
                rental__rent_type=rent_type
            )
        else:
            return PaymentSchedule.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        rent_type = self.request.query_params.get('rent_type', 'daily')
        today = timezone.localdate()
        data = []

        filtered_schedules = queryset.filter(payment_date__lt=today)
        data.append({
            'date': 'unpaid',
            'payment_schedules': PaymentScheduleListSerializer(filtered_schedules.order_by('-due_date'), many=True).data
        })

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
        return super().get_queryset().filter(is_active=False, bad_rental=False)


@method_decorator(csrf_exempt, name='dispatch')
class NoActiveBadRentalListAPIView(generics.ListAPIView):
    queryset = Rental.objects.all()
    serializer_class = NoActiveRentalListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(is_active=False, bad_rental=True)


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
    permission_classes = [permissions.IsAuthenticated]

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
            payment.employee = request.user
            payment.save()

            rental = payment.rental
            payment_schedules = PaymentSchedule.active_objects.filter(rental=rental)
            if payment_schedules.count() == 0:
                rental.is_active = False
                rental.closing_date = timezone.now().date()
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


@method_decorator(csrf_exempt, name='dispatch')
class GeneratePDF(APIView):

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter(
            'rent_id', openapi.IN_QUERY, description="Ijara ID",
            type=openapi.TYPE_INTEGER
        )
    ])
    def get(self, request, *args, **kwargs):
        rent_id = request.query_params.get('rent_id')
        if not rent_id:
            return Response(data={'detail': 'Ijara ID kerak'}, status=400)

        try:
            rental = Rental.objects.get(id=rent_id)
        except Rental.DoesNotExist:
            return Response(data={'detail': 'Ijara topilmadi'}, status=404)

        serializer = RentalRetrieveSerializer(rental)
        pdf_path = pdf_writer(serializer.data)

        with open(pdf_path, 'rb') as pdf:
            pdf = pdf.read()
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="rent-{rental.id}.pdf"'
            return response


@method_decorator(csrf_exempt, name='dispatch')
class BlacklistNoActiveRentalAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'rental_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Ijara ID')
            },
            required=['rental_id']
        ),
        responses={
            200: openapi.Response(description='Ijara qora ro\'yxatga tushurildi'),
            400: openapi.Response(description='Ijara ID kerak'),
            404: openapi.Response(description='Ijara topilmadi')
        }
    )
    def post(self, request):
        rental_id = request.data.get('rental_id')
        if rental_id is None:
            return Response(data={'detail': 'Ijara ID kerak'}, status=400)
        try:
            rental = Rental.objects.get(id=rental_id, is_active=False, bad_rental=False)
        except Rental.DoesNotExist:
            return Response(data={'detail': 'Ijara topilmadi'}, status=404)
        rental.bad_rental = True
        rental.save()
        return Response(data={'message': 'Ijara qora ro\'yxatga tushurildi'}, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class ClosingActiveRentalAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'rental_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Ijara ID')
            },
            required=['rental_id']
        ),
        responses={
            200: openapi.Response(description='Ijara yopildi'),
            400: openapi.Response(description='Ijara ID kerak'),
            404: openapi.Response(description='Ijara topilmadi')
        }
    )
    def post(self, request):
        rental_id = request.data.get('rental_id')
        if rental_id is None:
            return Response(data={'detail': 'Ijara ID kerak'}, status=400)
        try:
            rental = Rental.active_objects.get(id=rental_id)
        except Rental.DoesNotExist:
            return Response(data={'detail': 'Ijara topilmadi'}, status=404)

        rental.is_active = False
        rental.closing_date = timezone.now().date()
        rental.save()
        payment_schedules = PaymentSchedule.active_objects.filter(rental=rental)
        for payment in payment_schedules:
            payment.is_paid = True
            payment.amount = payment.amount_paid
            payment.penalty_amount = Decimal('0.0')
            payment.paid_date = timezone.now()
            payment.payment_closing_date = timezone.now()
            payment.save()
        if rental.rent_type == 'credit':
            car = rental.car
            car.status = 'sold'
            car.is_active = False
        else:
            car = rental.car
            car.status = 'active'
        car.save()
        return Response(data={'message': 'Ijara yopildi'}, status=200)


# @method_decorator(csrf_exempt, name='dispatch')
# class UnPaidPaymentScheduleDashboardView(generics.ListAPIView):
#     queryset = PaymentSchedule.active_objects.all()
#     serializer_class = PaymentScheduleListSerializer
#
#     def get_queryset(self):
#         now = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
#         print(now)
#         return PaymentSchedule.active_objects.filter(due_date__lte=now, is_paid=False)

