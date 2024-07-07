from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Rental
from rent_app.serializers import RentalDashboardSerializer


class DashboardRentalsView(APIView):
    serializer_class = RentalDashboardSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'rent_type',
                openapi.IN_QUERY,
                description="Ijara turi bo'yicha filter",
                type=openapi.TYPE_STRING,
                enum=['daily', 'monthly', 'credit']
            )
        ],
        responses={
            200: RentalDashboardSerializer(many=True)
        }
    )
    def get(self, request):
        rent_type = request.query_params.get('rent_type', None)
        rentals = Rental.active_objects.all()

        if rent_type:
            rentals = rentals.filter(rent_type=rent_type)
        else:
            rentals = rentals.filter(rent_type='daily')

        serializer = self.serializer_class(rentals, many=True)
        return Response(serializer.data)
