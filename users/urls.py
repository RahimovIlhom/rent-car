from django.urls import path
from .views import RegisterUserView, LoginView, LogoutView, ChangePasswordView, ResetPasswordView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
]
