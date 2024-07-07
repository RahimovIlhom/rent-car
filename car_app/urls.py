from django.urls import path

from car_app import views

urlpatterns = [
    path('create/', views.CarCreateAPIView.as_view()),
    path('unrepaired/', views.UnRepairedCarsListAPIView.as_view()),
    path('activate/', views.ActivateCarAPIView.as_view()),
    path('deactivate/', views.DeActivateCarAPIView.as_view()),
    path('list/', views.CarListAPIView.as_view()),
    path('active/list/', views.ActiveCarListAPIView.as_view()),
    path('detail/<int:car_id>/', views.CarDetailAPIView.as_view()),
    path('update/<int:car_id>/', views.CarUpdateAPIView.as_view()),
    path('delete/<int:car_id>/', views.CarDeleteAPIView.as_view()),
]
