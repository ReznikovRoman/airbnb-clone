from channels.http import AsgiHandler
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

import chat_bot.routing


application = ProtocolTypeRouter(
    application_mapping={
        # Django's ASGI application to handle traditional HTTP requests
        "http": AsgiHandler,

        # WebSocket chat handler
        'websocket': AuthMiddlewareStack(
            URLRouter(
                chat_bot.routing.websocket_urlpatterns,
            ),
        ),
    },
)
