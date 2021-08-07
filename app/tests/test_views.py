import json
import datetime
from rest_framework import status
from django.test import TestCase, Client
from django.urls import reverse
from ..models import Music
from ..serializers import MusicSerializer

client = Client()

class GetAllMusicsTest(TestCase):

    def setUp(self):
        Music.objects.create(
            title='Title 1', artist='Artist 1', release_date='2021-01-01', duration=datetime.timedelta(seconds=71))
        Music.objects.create(
            title='Title 2', artist='Artist 2', release_date='2021-01-01', duration=datetime.timedelta(seconds=71), number_views=2)
        Music.objects.create(
            title='Title 3', artist='Artist 3', release_date='2021-01-01', duration=datetime.timedelta(seconds=71), feat=True)
        Music.objects.create(
            title='Title 4', artist='Artist 4', release_date='2021-01-01', duration=datetime.timedelta(seconds=71))
        Music.objects.create(
            title='Title 5', artist='Artist 5', release_date='2021-01-01', duration=datetime.timedelta(seconds=71))

    def test_get_all_musics(self):
        response = client.get(reverse('get_post_musics'))
        musics = Music.objects.all()
        serializer = MusicSerializer(musics, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)