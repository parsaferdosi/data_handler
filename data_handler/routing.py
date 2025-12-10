from django.urls import path
from . import consumers
#Path routing for websockets
websocket_urlpatterns = [
    path('ws/root/', consumers.RootConsumer.as_asgi()),
]