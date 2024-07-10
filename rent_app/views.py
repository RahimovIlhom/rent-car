from django_filters import rest_framework as filters
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics

from rent_app.filters import PaymentScheduleFilter
from rent_app.models import PaymentSchedule
from rent_app.serializers import PaymentScheduleDashboardSerializer


class PaymentScheduleDashboardView(generics.ListAPIView):
    queryset = PaymentSchedule.objects.all()
    serializer_class = PaymentScheduleDashboardSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = PaymentScheduleFilter

    def get_queryset(self):
        queryset = PaymentSchedule.active_objects.all()
        return queryset

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter(
            'rent_type', openapi.IN_QUERY, description="Filter ijara turi bo'yicha",
            type=openapi.TYPE_STRING, enum=['daily', 'monthly', 'credit'],
        ),
        openapi.Parameter(
            'year', openapi.IN_QUERY, description="Filter yil bo'yicha",
            type=openapi.TYPE_INTEGER
        ),
        openapi.Parameter(
            'month', openapi.IN_QUERY, description="Filter oy bo'yicha",
            type=openapi.TYPE_INTEGER
        ),
        openapi.Parameter(
            'day', openapi.IN_QUERY, description="Filter kun bo'yicha",
            type=openapi.TYPE_INTEGER
        ),
    ])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
