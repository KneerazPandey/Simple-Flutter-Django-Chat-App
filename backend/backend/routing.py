import chats.routing

websocket_urlpatterns = [
    
]

websocket_urlpatterns.extend(chats.routing.websocket_urlpatterns)