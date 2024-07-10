from django.urls import path

from .views import RegisterUserView, LoginView, LogoutView, ChangePasswordView, ResetPasswordView, UserListAPIView, \
    EmployeeUpdateAPIView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('employees/', UserListAPIView.as_view(), name='users'),
    path('employee/update/', EmployeeUpdateAPIView.as_view(), name='employee_update'),
]
