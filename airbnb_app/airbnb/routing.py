from channels.auth import AuthMiddlewareStack
from channels.http import AsgiHandler
from channels.routing import ProtocolTypeRouter, URLRouter

from django.conf import settings

import chat_bot.routing


if not settings.DEBUG:
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
else:
    application = ProtocolTypeRouter(
        application_mapping={
            # WebSocket chat handler
            'websocket': AuthMiddlewareStack(
                URLRouter(
                    chat_bot.routing.websocket_urlpatterns,
                ),
            ),
        },
    )
