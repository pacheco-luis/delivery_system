from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # re_path(r"ws/notify/", consumers.NotificationConsumer.as_asgi()),
    re_path(r'^ws/notify/(?P<user_id>[0-9a-f-]+)/$', consumers.NotificationConsumer.as_asgi()),
]