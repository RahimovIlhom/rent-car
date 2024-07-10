from django.urls import path

from rent_app import views

urlpatterns = [
    path('dashboard/', views.PaymentScheduleDashboardView.as_view()),
    path('create/', views.RentalCreateAPIView.as_view()),
    path('list/', views.RentalListAPIView.as_view()),
    path('retrieve/<int:pk>/', views.RentalRetrieveAPIView.as_view()),
]
