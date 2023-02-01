from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import async_to_sync
from . models import Conversation, Message
from django.contrib.auth.models import User
from . serializers import MessageSerializer


class ChatConsumer(JsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.conversation_name = None
        self.conversation = None 
        
    def connect(self):
        print('Connected .......')
        self.room_name = "home"
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            return
        
        self.accept()
        self.conversation_name = f"{self.scope['url_route']['kwargs']['conversation_name']}"
        self.conversation, created = Conversation.objects.get_or_create(name=self.conversation_name)
        async_to_sync(self.channel_layer.group_add)(self.conversation_name, self.channel_name)
        self.send_json(
            {
                'type': "welcome_message",
                "message": "Hey there? You've sucessfully connected",
            }
        ) 
        
    def receive_json(self, content, **kwargs):
        print('Data Reveived .......')
        message_type = content['type']
        if message_type == 'greeting':
            async_to_sync(self.channel_layer.group_send)(
                self.conversation_name, 
                {
                    'type': 'chat_message_echo',
                    'name': content['name'],
                    'message': content['message'],
                }
            )
        
        if message_type == 'chat_message':
            async_to_sync(self.channel_layer.group_send)(
                self.conversation_name, 
                {
                    'type': 'chat_message',
                    'from_user': content['from_user'],
                    'to_user': content['to_user'],
                    'content': content['message'],
                }
            )
            message = Message.objects.create(
                from_user = self.user,
                to_user = self.get_receiver(),
                content = content['message'],
                conversation = self.conversation
            )
            message.save()
        
        if message_type == 'get_message_history':
            messages = self.conversation.messages.all().order_by('-timestamp')
            async_to_sync(self.channel_layer.group_send)(
                self.conversation_name,
                {
                    'type': 'get_message_history',
                    'messages': MessageSerializer(messages, many=True).data,
                }
            )
            
        if message_type == 'typing':
            async_to_sync(self.channel_layer.group_send)(
                self.conversation_name,
                {
                    'type': 'typing',
                    'user': self.user.username,
                    'typing': True,
                    'message': f'{self.user.username} is typing .......'
                }
            )
            
        if message_type == 'stop_typing':
            async_to_sync(self.channel_layer.group_send)(
                self.conversation_name,
                {
                    'type': 'stop_typing',
                    'user': self.user.username,
                    'typing': False,
                    'message': '',
                }
            )
            
        return super().receive_json(content, **kwargs)
    
    def get_receiver(self):
        usernames = self.conversation_name.split('_')
        for username in usernames:
            if username != self.user.username:
                return User.objects.get(username=username)
    
    def chat_message(self, event):
        print(event)
        self.send_json(event)
        
    def get_message_history(self, event):
        print(event)
        self.send_json(event)
    
    def chat_message_echo(self, event):
        print(event)
        self.send_json(event)
        
    def typing(self, event):
        print(event)
        self.send_json(event)
        
    def stop_typing(self, event):
        print(event)
        self.send_json(event)
        
    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.conversation_name,
            self.channel_name,
        )
        return super().disconnect(code)