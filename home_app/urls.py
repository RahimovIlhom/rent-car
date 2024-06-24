from django.urls import path

from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('admin-login/', views.custom_login, name='admin-login'),
    path('accounts/logout/', views.custom_logout, name='admin-logout'),
]
