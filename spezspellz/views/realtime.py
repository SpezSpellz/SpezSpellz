"""Implements real time communication between client and server."""
from json import dumps
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import BaseChannelLayer


class RealtimeConsumer(AsyncWebsocketConsumer):
    """React to realtime stuff."""

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user_id = None
        self.channels = []

    async def connect(self):
        user = self.scope['user']
        if not user.is_authenticated:
            await self.accept()
            await self.close(code=3000)
        self.user_id = user.pk
        await self.channel_layer.group_add(
            f"user_{self.user_id}", self.channel_name
        )
        self.channels = [
            name for name in self.scope['url_route']['kwargs']
            .get('channels', '').split('|')
            if name and len(name) < BaseChannelLayer.MAX_NAME_LENGTH
            and bool(BaseChannelLayer.group_name_regex.match(name))
        ]
        for channel in self.channels:
            await self.channel_layer.group_add(channel, self.channel_name)
        await self.accept()

    async def disconnect(self, _):
        for channel in self.channels:
            await self.channel_layer.group_discard(channel, self.channel_name)
        await self.channel_layer.group_discard(
            f"user_{self.user_id}", self.channel_name
        )

    async def realtime(self, event):
        """Send realtime message."""
        if self.user_id == event.get('except'):
            return
        await self.send(text_data=dumps(event['data']))
