from dateutil.relativedelta import relativedelta
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from datetime import date, timedelta
from rest_framework import generics, permissions

from rent_app.models import PaymentSchedule, Rental
from rent_app.serializers import PaymentScheduleDashboardSerializer, PaymentScheduleListSerializer, \
    CreateRentalSerializer, ActiveRentalListSerializer


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


class PaymentScheduleDashboardView(generics.ListAPIView):
    serializer_class = PaymentScheduleDashboardSerializer

    def get_queryset(self):
        rent_type = self.request.query_params.get('rent_type')
        today = timezone.localdate()

        if rent_type == 'daily':
            end_date = today + timedelta(days=3)
            return PaymentSchedule.objects.filter(
                payment_date__range=(today, end_date),
                rental__rent_type=rent_type
            )
        elif rent_type in ['monthly', 'credit']:
            start_date = today.replace(day=1)
            end_date = start_date + relativedelta(months=3)
            return PaymentSchedule.objects.filter(
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


class RentalCreateAPIView(generics.CreateAPIView):
    queryset = Rental.active_objects.all()
    serializer_class = CreateRentalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(data=serializer.data, status=201, headers=headers)


class RentalListAPIView(generics.ListAPIView):
    queryset = Rental.active_objects.all()
    serializer_class = ActiveRentalListSerializer
    permission_classes = [permissions.IsAuthenticated]
