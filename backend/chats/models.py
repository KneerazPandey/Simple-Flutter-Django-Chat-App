from django.db import models
from django.contrib.auth.models import User 


class Conversation(models.Model):
    name = models.CharField(max_length=128)
    online = models.ManyToManyField(User, blank=True)
    
    
    def get_online_count(self):
        return self.online.count()
    
    def join(self, user):
        self.online.add(user)
        self.save()
        
    def leave(self, user):
        self.online.remove(user)
        self.save()
        
    def __str__(self):
        return f'{self.name} {self.get_online_count()}'
    


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_from_me')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_to_me')
    content = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    
    def __str__(self):
        return f'From {self.from_user.username} to {self.to_user.username} : {self.content} {self.timestamp}'