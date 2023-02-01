from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status, generics
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from . serializers import UserSerializer, MessageSerializer
from . models import Conversation, Message


class LoginAPIView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    
    def post(self, request: Request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        if user is None:
            return Response(data={'error': 'Invalid username and password'}, status=status.HTTP_400_BAD_REQUEST)
        
        refresh_token = RefreshToken.for_user(user)
        data = {
            'id': int(user.id),
            'username': user.username,
            'tokens': dict({
                'refresh_token': str(refresh_token),
                'access_token': str(refresh_token.access_token),
            }),
        }
        return Response(data=data, status=status.HTTP_200_OK)
        
        

class GetAllUserAPIView(generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get(self, request: Request):
        users = User.objects.exclude(username=self.request.user.username)
        serializer = self.serializer_class(users, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK) 
    
    
class GetAllUserMessagesAPIView(generics.GenericAPIView):
    def get(self, request: Request, friend_name: str):
        datas = [request.user.username, friend_name]
        datas.sort()
        
        conversation_name = f'{datas[0]}_{datas[1]}'

        conversation = Conversation.objects.get(name=conversation_name)
        messages = Message.objects.filter(conversation=conversation)
        serializers = MessageSerializer(messages, many=True)
        outputs = []
        
        for data in serializers.data:
            out = {
                'content': data['content'],
                'id': data['id'],
                'timestamp': data['timestamp']
            }
            from_user = User.objects.get(id=data['from_user'])
            out['from_user'] = from_user.username
            
            to_user = User.objects.get(id=data['to_user'])
            out['to_user'] = to_user.username
            outputs.append(out)
            
        return Response(data=outputs, status=status.HTTP_200_OK)