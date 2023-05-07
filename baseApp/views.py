from django.shortcuts import render,redirect
from .models import Room,Topic,Message,User
from .forms import RoomForm,UserForm,CustomUserCreationForm
from django.db.models import Q
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
import re
# Create your views here.

def loginPage(request):
    page='login'
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method=='POST':
        email=request.POST.get('email').lower()
        password=request.POST.get('password')
        
        try:
            user=User.objects.get(email=email)
        except:
            messages.error(request,'User does not exist')
        
        user=authenticate(request,email=email,password=password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'email or Password does not exist')
    context={'page':page}
    return render(request,'baseApp/login_register.html',context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    form = CustomUserCreationForm()
    
    if request.method=='POST':
        form=CustomUserCreationForm(request.POST,request.FILES)
        if form.is_valid():
            user=form.save(commit=False)
            user.username=user.username.lower()
            user.save()
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'an error occured during registration')
            
    
    return render(request,'baseApp/login_register.html',{'form':form})

def home(request):
    q=request.GET.get('q') if request.GET.get('q') !=None else ''
    rooms=Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
        )
    room_count=rooms.count()
    topics=Topic.objects.all()[0:5]
    room_messages=Message.objects.filter(Q(room__name__icontains=q))
    context={'rooms':rooms,'topics':topics,'room_count':room_count,'room_messages':room_messages}
    return render(request,'baseApp/home.html',context)

def room(request,pk):
    room=Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants=room.participants.all()
    if request.method=='POST':
        message=Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room',pk=room.id)
    
    context={'room':room,'room_messages':room_messages,'participants':participants}
    return render(request,'baseApp/room.html',context)

def userProfile(request,pk):
    user=User.objects.get(id=pk)
    rooms=user.room_set.all()
    room_messages=user.message_set.all()
    topics=Topic.objects.all()
    context={'user':user,'rooms':rooms,'room_messages':room_messages,'topics':topics}
    return render(request,'baseApp/profile.html',context)

@login_required(login_url='login')
def createRoom(request):
    page='create'
    form=RoomForm()
    topics=Topic.objects.all()
    if request.method=='POST':
        topic_name=request.POST.get('topic')
        topic,created=Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        return redirect('home')
    context={'form':form,'topics':topics,'page':page}
    return render(request,'baseApp/room_form.html',context)

@login_required(login_url='login')
def updateRoom(request,pk):
    page='register'
    room=Room.objects.get(id=int(pk))
    form=RoomForm(instance=room)
    topics=Topic.objects.all()
    
    if request.user!=room.host:
        return HttpResponse('You are not allowed here!!')
    
    if request.method=='POST':
        topic_name=request.POST.get('topic')
        topic,created=Topic.objects.get_or_create(name=topic_name)
        form = RoomForm(request.POST, instance=room)
        room.name=request.POST.get('name')
        room.topic=topic
        room.description=request.POST.get('description')
        room.save()
        return redirect(home)
    
    context={'form':form,'topics':topics,'page':page}
    return render(request,'baseApp/room_form.html',context)

@login_required(login_url='login')
def deleteRoom(request,pk):
    room=Room.objects.get(id=int(pk))
    if request.method=='POST':
        room.delete()
        return redirect('home')
    return render(request,'baseApp/delete.html',{'obj':room})

@login_required(login_url='login')
def deleteMessage(request,pk):
    post_message=Message.objects.get(id=int(pk))
    
    if request.user != post_message.user:
        return HttpResponse('You are not allowed here!!!')
    
    if request.method=='POST':
        post_message.delete()
        return redirect('home')
    context={'obj': post_message}
    return render(request,'baseApp/delete.html',context)

@login_required(login_url='login')
def updateUser(request):
    user=request.user
    form=UserForm(instance=user)
    
    if request.method=='POST':
        form=UserForm(request.POST,request.FILES,instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile',pk=user.id)    
    context={'form':form}
    return render(request,'baseApp/update-user.html',context)
    
    
def topicsPage(request):
    q=request.GET.get('q') if request.GET.get('q') !=None else ''
    topics=Topic.objects.filter(name__icontains=q)
    context={'topics':topics}
    return render(request,'baseApp/topics.html',context)

def activityPage(request):
    activity_messages=Message.objects.all()
    context={'activity_messages':activity_messages}
    return render(request,'baseApp/activity.html',context)