from channels.generic.websocket import AsyncJsonWebsocketConsumer


class AdminNotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        if not user.is_authenticated:
            await self.close()
            return

        self.user_group = f"admin_user_{user.id}"
        await self.channel_layer.group_add(self.user_group, self.channel_name)

        if user.is_superuser:
            await self.channel_layer.group_add('admin_superusers', self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.user_group, self.channel_name)
        if self.scope['user'].is_superuser:
            await self.channel_layer.group_discard('admin_superusers', self.channel_name)

    async def notify(self, event):
        # ожидается, что event содержит 'message'
        await self.send_json(event['message'])
