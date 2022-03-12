import datetime

from asgiref.sync import sync_to_async
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from model_bakery import baker

from django.test import TransactionTestCase
from django.urls import re_path

from hosts.models import RealtyHost
from realty.models import Realty

from .consumers import ChatBotConsumer


class ChatBotConsumerTests(TransactionTestCase):
    serialized_rollback = True
    application = URLRouter([
        re_path(r'ws/chat-bot/$', ChatBotConsumer.as_asgi(), name='chat_bot'),
    ])

    def create_test_realty(self) -> Realty:
        test_user = baker.make('CustomUser')

        test_host = RealtyHost.objects.create(user=test_user)
        test_host.save()

        test_address = baker.make(
            _model='Address',
            city='Moscow',
        )

        test_realty = baker.make(
            'Realty',
            location=test_address,
            host=test_host,
            is_available=True,
        )

        return test_realty

    async def test_consumer_connects_correctly(self):
        """Consumer connects to a correct url."""
        communicator = WebsocketCommunicator(self.application, '/ws/chat-bot/')
        connected, subprotocol = await communicator.connect()

        self.assertTrue(connected)

        await communicator.disconnect()

    async def test_send_message_on_connect(self):
        """Consumer sends a default message on connect."""
        communicator = WebsocketCommunicator(self.application, '/ws/chat-bot/')
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        response = await communicator.receive_json_from()
        self.assertEqual(
            response['message'],
            "Hi! I'm an Air Helper. Type `city` to see how many available places are there.",
        )

        await communicator.disconnect()

    async def test_correct_response_no_realty(self):
        """Response is properly formatted if there are no places in the city specified by a user."""
        communicator = WebsocketCommunicator(self.application, '/ws/chat-bot/')
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        await communicator.send_json_to({
            'type': 'chat_bot_message',
            'message': "moscow",
            'is_message_from_user': True,
            'datetime': datetime.datetime.now().isoformat(),
        })

        await communicator.receive_json_from()  # welcome message
        await communicator.receive_json_from()  # user message
        chat_bot_response = await communicator.receive_json_from()

        assert chat_bot_response['message'] == 'There are no available places in Moscow.'

        await communicator.disconnect()

    async def test_correct_response_realty_exists(self):
        """Response is correct if there are some places in the city specified by the user."""
        await sync_to_async(self.create_test_realty, thread_sensitive=True)()  # realty city input message

        communicator = WebsocketCommunicator(self.application, '/ws/chat-bot/')
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        await communicator.send_json_to({
            'type': 'chat_bot_message',
            'message': "moscow",
            'is_message_from_user': True,
            'datetime': datetime.datetime.now().isoformat(),
        })

        await communicator.receive_json_from()  # welcome message
        await communicator.receive_json_from()  # user message
        chat_bot_response = await communicator.receive_json_from()

        assert chat_bot_response['message'] == 'There is 1 available place in Moscow.'

        await communicator.disconnect()
