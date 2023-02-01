from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.LoginAPIView.as_view(), name='login',),
    
    path('users/', views.GetAllUserAPIView.as_view(), name='users',),
    
    path('chats/<str:friend_name>/', views.GetAllUserMessagesAPIView.as_view(), name='messages',),
]
