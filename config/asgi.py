import os

from django.core.asgi import get_asgi_application

import api.v1.chat.routing
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(api.v1.chat.routing.websocket_urlpatterns)
        ),
    }
)
