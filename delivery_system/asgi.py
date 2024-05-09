"""
ASGI config for delivery_system project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from notifications.routing import websocket_urlpatterns as notifications_ws_urlp
from chatbot.routing import websocket_urlpatterns as chatbot_ws_urlp

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_system.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
            URLRouter( routes= notifications_ws_urlp + chatbot_ws_urlp )
        ),
})
