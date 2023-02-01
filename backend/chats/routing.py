from django.urls import path
from . consumers import ChatConsumer


websocket_urlpatterns = [
    path('<str:conversation_name>/', ChatConsumer.as_asgi(),),
]