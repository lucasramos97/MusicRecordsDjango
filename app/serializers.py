from rest_framework import serializers
from .models import Music, User


class MusicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Music
        exclude = ['user']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
