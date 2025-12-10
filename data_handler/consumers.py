from channels.generic.websocket import AsyncWebsocketConsumer
import json

"""
WebSocket consumer to handle real-time notifications via Django Channels.
"""

class RootConsumer(AsyncWebsocketConsumer):
    group_name = "root_group"

    async def connect(self):
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        await self.send(text_data=json.dumps(text_data["data"]))