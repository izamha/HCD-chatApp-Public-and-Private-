"""
ASGI config for hcd project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from django.urls import re_path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hcd.settings')
django_asgi_app = get_asgi_application()

# Channels Imports
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from chat.consumers import ChatConsumer, GroupChatConsumer
from chat.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    # Django's ASGI application to handle traditional HTTP requests
    "http": django_asgi_app,

    # WebSocket chat handler
    "websocket": AuthMiddlewareStack(
        URLRouter([
            re_path(
                r"ws/chat/(?P<public_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$",
                ChatConsumer.as_asgi()),
            re_path(r"ws/chat/(?P<group_id>[0-9]+)/$", GroupChatConsumer.as_asgi()),
        ])
    ),
})

# re_path(r"^(en-us)/ws/chat/(?P<group_id>[0-9]+)/$", GroupChatConsumer.as_asgi()),

