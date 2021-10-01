from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    username = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class Music(models.Model):
    class Meta:
        db_table = 'musics'
        ordering = ['artist', 'title']

    title = models.CharField(max_length=100)
    artist = models.CharField(max_length=100)
    release_date = models.DateField()
    duration = models.TimeField()
    number_views = models.IntegerField(null=True, blank=True, default=0)
    feat = models.BooleanField(null=True, blank=True, default=False)
    deleted = models.BooleanField(null=True, blank=True, default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
