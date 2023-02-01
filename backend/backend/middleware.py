from urllib.parse import parse_qs
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from jwt import decode
from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser
from channels.db import database_sync_to_async


class TokenAuthenticationMiddleware:
    def __init__(self, app):
        self.app = app 
        
    async def __call__(self, scope, receive, send):
        query_stirng = scope['query_string']
        query_params = query_stirng.decode()
        query_dict = parse_qs(query_params)
        token = query_dict['token'][0]
        
        try:
            UntypedToken(token)
        except (InvalidToken, TokenError):
            scope['user'] = AnonymousUser
            return await self.app(scope, receive, send)
        else:
            decoded_data =decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = await database_sync_to_async(User.objects.get)(id=decoded_data['user_id'])
            scope['user'] = user
        
        return await self.app(scope, receive, send)