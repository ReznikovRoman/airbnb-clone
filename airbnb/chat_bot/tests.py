import datetime

from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator

from django.test import TransactionTestCase
from django.urls import re_path
from asgiref.sync import sync_to_async

from hosts.models import RealtyHost
from realty.models import Realty
from accounts.models import CustomUser
from addresses.models import Address
from .consumers import ChatBotConsumer


class ChatBotConsumerTests(TransactionTestCase):
    serialized_rollback = True
    application = URLRouter([
        re_path(r'ws/chat-bot/$', ChatBotConsumer.as_asgi(), name='chat_bot'),
    ])

    def create_test_realty(self) -> Realty:
        test_user = CustomUser.objects.create_user(
            email='host@gmail.com',
            first_name='John',
            last_name='Doe',
            password='123',
        )
        test_user.save()
        test_host = RealtyHost.objects.create(user=test_user)
        test_host.save()
        test_address = Address.objects.create(country='Russia', city='Moscow', street='Moscow, Ulitsa Zorge')
        test_address.save()
        test_realty = Realty.objects.create(
            name='SMART HOST | Bright studio | 2 guests',
            slug='smart-host-bright-studio-2-guests',
            description='Comfortable and cozy apartment situated in the centre of the city, 21 floor. '
                        'One of the best views paired with perfect location.',
            realty_type='Apartments',
            beds_count=2,
            max_guests_count=4,
            price_per_night=65,
            location=test_address,
            host=test_host,
            is_available=True
        )
        test_realty.save()
        return test_realty

    async def test_consumer_connects_correctly(self):
        communicator = WebsocketCommunicator(self.application, '/ws/chat-bot/')
        connected, subprotocol = await communicator.connect()

        self.assertTrue(connected)

        await communicator.disconnect()

    async def test_send_message_on_connect(self):
        communicator = WebsocketCommunicator(self.application, '/ws/chat-bot/')
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        response = await communicator.receive_json_from()
        self.assertEqual(
            response['message'],
            "Hi! I'm an Airbnb Helper. Type `city` to see how many available places are there."
        )

        await communicator.disconnect()

    async def test_correct_response_no_realty(self):
        communicator = WebsocketCommunicator(self.application, '/ws/chat-bot/')
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        await communicator.send_json_to({
            'type': 'chat_bot_message',
            'message': "moscow",
            'is_message_from_user': True,
            'datetime': datetime.datetime.now().isoformat(),
        })

        welcome_message = await communicator.receive_json_from()
        user_message = await communicator.receive_json_from()
        chat_bot_response = await communicator.receive_json_from()

        assert chat_bot_response['message'] == 'There are no available places in Moscow.'

        await communicator.disconnect()

    async def test_correct_response_realty_exists(self):
        realty = await sync_to_async(self.create_test_realty, thread_sensitive=True)()

        communicator = WebsocketCommunicator(self.application, '/ws/chat-bot/')
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        await communicator.send_json_to({
            'type': 'chat_bot_message',
            'message': "moscow",
            'is_message_from_user': True,
            'datetime': datetime.datetime.now().isoformat(),
        })

        welcome_message = await communicator.receive_json_from()
        user_message = await communicator.receive_json_from()
        chat_bot_response = await communicator.receive_json_from()

        assert chat_bot_response['message'] == 'There is 1 available place in Moscow.'

        await communicator.disconnect()
