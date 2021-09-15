from rest_framework import serializers
from app.models import Music, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']


class MusicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Music
        exclude = ['deleted', 'user']
