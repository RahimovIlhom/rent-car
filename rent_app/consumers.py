import json
from channels.generic.websocket import AsyncWebsocketConsumer


class PaymentScheduleConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'payment_schedules'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        # Process received data

    async def send_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))
