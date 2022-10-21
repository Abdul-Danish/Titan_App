from sys import maxsize
from unittest.util import _MAX_LENGTH
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Topic(models.Model):

    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Room(models.Model):

    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)

    participants = models.ManyToManyField(User, related_name="participants", blank=True)
    
    updated = models.DateTimeField(auto_now=True)       # Updates every time it saves
    created = models.DateTimeField(auto_now_add=True)   # Tells when the room was created

    class Meta:     # ordering rooms based on created / updated
        ordering = ['-updated', '-created']

    def __str__(self):
        return str(self.name)


class Message(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)    # one to many relationship
    room = models.ForeignKey(Room, on_delete=models.CASCADE)    # one to many relationship
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.body[0:50]

