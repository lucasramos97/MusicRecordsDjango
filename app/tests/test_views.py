from rest_framework import status
from django.test import TestCase, Client
from django.urls import reverse
from .factories import MusicFactory

client = Client()

class GetAllMusicsTest(TestCase):

    def setUp(self):
        MusicFactory.create_batch(10)

    def test_get_all_musics_with_default_query_params(self):
        response = client.get(reverse('get_post_musics'))
        self.assertIsNotNone(response.data['content'])
        self.assertEqual(len(response.data['content']), 5)
        self.assertEqual(response.data['total'], 10)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_musics_with_query_params(self):
        response = client.get(reverse('get_post_musics'), {'page': 2, 'size': 4})
        self.assertIsNotNone(response.data['content'])
        self.assertEqual(len(response.data['content']), 4)
        self.assertEqual(response.data['total'], 10)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
