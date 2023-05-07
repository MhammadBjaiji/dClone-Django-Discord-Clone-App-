from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Room
from .models import User


class RoomForm(ModelForm):
    class Meta:
        model=Room
        fields='__all__'
        exclude=['host','participants']
        
        

class UserForm(ModelForm):
    class Meta:
        model=User
        fields=['avatar','name','username','email','bio']
        

class CustomUserCreationForm(UserCreationForm):
    
    class Meta:
        model=User
        fields = ('avatar','name','username','email', 'bio', 'password1', 'password2')