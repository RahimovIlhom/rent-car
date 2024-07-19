from django.shortcuts import render
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rent_app.models import Rental
from .serializers import PaymentCreateSerializer, RentalPaymentsListSerializer
from .models import Payment
from rest_framework import generics


class PaymentCreateAPIView(generics.CreateAPIView):
    serializer_class = PaymentCreateSerializer
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated]


class RentalPaymentsListAPIView(generics.ListAPIView):
    serializer_class = RentalPaymentsListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = []

    def get_queryset(self):
        rental_id = self.kwargs.get('rental_id')
        if not rental_id:
            raise NotFound("rental_id parametri talab qilinadi")
        try:
            rental = Rental.objects.get(pk=rental_id)
        except Rental.DoesNotExist:
            raise NotFound("Ijara shartnomasi topilmadi")
        return Payment.objects.filter(rental=rental)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'rental_id',
                openapi.IN_PATH,
                description="ID of the rental",
                type=openapi.TYPE_INTEGER,
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
