from django.urls import path

from rent_app import views

urlpatterns = [
    path('dashboard/', views.PaymentScheduleDashboardView.as_view()),
]
