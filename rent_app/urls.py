from django.urls import path

from rent_app import views

urlpatterns = [
    path('dashboard/', views.PaymentScheduleDashboardView.as_view()),
    # path('dashboard/unpaid/', views.UnPaidPaymentScheduleDashboardView.as_view()),
    path('create/', views.RentalCreateAPIView.as_view()),
    path('active/list/', views.ActiveRentalListAPIView.as_view()),
    path('active/rental/closing/', views.ClosingActiveRentalAPIView.as_view()),
    path('noactive/list/', views.NoActiveRentalListAPIView.as_view()),
    path('noactive/rental/blacklisting/', views.BlacklistNoActiveRentalAPIView.as_view()),
    path('noactive/blacklisted/list/', views.NoActiveBadRentalListAPIView.as_view()),
    path('retrieve/<int:pk>/', views.RentalRetrieveAPIView.as_view()),
    path('successfully_paid/', views.SuccessfullyPaidAPIView.as_view()),
    path('generate_pdf/', views.GeneratePDF.as_view()),
]
