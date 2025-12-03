from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/root/', consumers.RootConsumer.as_asgi()),
]