from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.PaymentCreateAPIView.as_view()),
    path('rentals/<int:rental_id>/payments/', views.RentalPaymentsListAPIView.as_view(), name='rental-payments-list'),
]
