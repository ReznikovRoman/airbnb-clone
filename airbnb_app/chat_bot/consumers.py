from typing import Union

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from django.utils import timezone

from realty.services.realty import get_available_realty_count_by_city


class ChatBotConsumer(AsyncJsonWebsocketConsumer):
    """Async json consumer that handles ChatBot messages."""

    async def connect(self):
        await self.accept()
        await self.channel_layer.send(
            self.channel_name,
            {
                'type': 'chat_bot_message',
                'message': "Hi! I'm an Air Helper. Type `city` to see how many available places are there.",
                'is_message_from_user': False,
                'datetime': timezone.now().isoformat(),
            },
        )

    async def receive_json(self, content: Union[dict, list, bool, float, int, str], **kwargs):
        if isinstance(content, dict):
            message = content.get('message', '')
        else:
            message = ''

        message_timestamp = timezone.now()

        response_message = await self.get_response_message(message)

        await self.channel_layer.send(
            self.channel_name,
            {
                'type': 'chat_bot_message',
                'message': message,
                'is_message_from_user': True,
                'datetime': message_timestamp.isoformat(),
            },
        )

        await self.channel_layer.send(
            self.channel_name,
            {
                'type': 'chat_bot_message',
                'message': response_message,
                'is_message_from_user': False,
                'datetime': message_timestamp.isoformat(),
            },
        )

    @database_sync_to_async
    def get_response_message(self, message: str):
        realty_count = get_available_realty_count_by_city(city=message)
        if realty_count:
            message_verb = 'is' if realty_count == 1 else 'are'
            pluralize = '' if realty_count == 1 else 's'
            return f"There {message_verb} {realty_count} available place{pluralize} in {message.capitalize()}."
        return f"There are no available places in {message.capitalize()}."

    async def chat_bot_message(self, event):
        await self.send_json(content=event)
