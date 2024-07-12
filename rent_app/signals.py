from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework.renderers import JSONRenderer
from .models import PaymentSchedule
from .serializers import PaymentScheduleListSerializer


@receiver(post_save, sender=PaymentSchedule)
def send_payment_schedule_update(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    serializer = PaymentScheduleListSerializer(instance)
    serialized_data = JSONRenderer().render(serializer.data)

    async_to_sync(channel_layer.group_send)(
        'payment_schedules',
        {
            'type': 'send_update',
            'data': serialized_data.decode('utf-8')
        }
    )
