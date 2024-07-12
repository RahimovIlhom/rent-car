from django.urls import re_path
from rent_app import consumers

websocket_urlpatterns = [
    re_path(r'ws/payment-schedule/$', consumers.PaymentScheduleConsumer.as_asgi()),
]
