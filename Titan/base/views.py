from ssl import _create_default_https_context
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse

from django.db.models import Q

from .models import Room, Topic, Message
from .forms import RoomForm
# Create your views here.

# rooms = [
#     {'id': 1, 'name': 'python programming'},
#     {'id': 2, 'name': 'java programming'},
# ]

def loginPage(request):
    page = 'login'

    if request.user.is_authenticated:         # prevents user who is already logedin to go to login page via url
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user = User.objects.get(username=username)      # check if user exists in database
        except:
            messages.error(request, 'Username or Password does not exist')

        user = authenticate(request, username=username, password=password)  

        if user is not None:        # if credentials are correct
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or Password does not exist')        

    context = {'page':page}
    return render(request, 'base/login_register.html', context)


def registerUser(request):
    form = UserCreationForm()       # default form provided by Django

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            login(request, form)
            return redirect('home')
        else:
            messages.error(request, 'Oops! an error occured during registering')

    context = {'form': form}
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | Q(name__icontains=q)
    )
    
    topics = Topic.objects.all()
    room_count = rooms.count()

    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count}
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()

    if request.method == "POST":
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {'room': room, 'room_messages': room_messages, 'participants': participants}
    return render(request, 'base/room.html', context)


def user_profile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()             # getting all the rooms that user has created
    topics = Topic.objects.all()

    context = {'user': user, 'rooms': rooms, 'topics': topics}
    return render(request, 'base/profile.html', context)


@login_required(login_url='login')
def create_room(request):
    form = RoomForm()

    if request.method == "POST":
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.host = request.user
            room.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/create_room.html', context)
 

@login_required(login_url='login')
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)          # fill the form based on current room values

    if request.user != room.host:
        return HttpResponse("You are not allowed here!")

    if request.method == "POST":
        form = RoomForm(request.POST, instance=room)        # updating current room fields using "instance=room"
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/create_room.html', context)


@login_required(login_url='login')
def delete_room(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("you are not allowed here!")

    if request.method == "POST":
        room.delete()
        return redirect('home')

    return render(request, 'base/delete.html', {'obj': room})


@login_required(login_url='login')
def delete_message(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse("you are not allowed here")

    if request.method == "POST":
        message.delete()
        return redirect('home')
    
    return render(request, 'base/delete.html', {'obj': message})



