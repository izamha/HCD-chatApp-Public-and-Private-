from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<group_id>[0-9]+)/$', consumers.GroupChatConsumer.as_asgi()),
]
