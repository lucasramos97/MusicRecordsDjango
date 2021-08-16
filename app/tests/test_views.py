import json
import datetime
from rest_framework import status
from django.test import TestCase, Client
from django.urls import reverse
from app.models import Music
from app.serializers import MusicSerializer
from .factories import MusicFactory

client = Client()

class GetAllMusicsTest(TestCase):

    def setUp(self):
        MusicFactory.create_batch(10)

    def test_get_all_musics_with_default_query_params(self):
        response = client.get(reverse('get_post_musics'))
        self.assertEqual(len(response.data['content']), 5)
        self.assertEqual(response.data['total'], 10)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_musics_with_explicit_query_params(self):
        response = client.get(reverse('get_post_musics'), {'page': 2, 'size': 4})
        self.assertEqual(len(response.data['content']), 4)
        self.assertEqual(response.data['total'], 10)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class GetMusicByIdTest(TestCase):

    def setUp(self):
        self.musics = MusicFactory.create_batch(10)
        self.deleted_musics = MusicFactory.create_batch(10, deleted=True)

    def test_get_music_by_id(self):
        response = client.get(reverse('get_update_delete_music', kwargs={'id': 1}))
        music = [music for music in self.musics if music.id == 1][0]
        serializer = MusicSerializer(music)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_nonexistent_music_by_id(self):
        response = client.get(reverse('get_update_delete_music', kwargs={'id': 100}))
        self.assertEqual(response.data['message'], 'Music not found!')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_get_deleted_music_by_id(self):
        deleted_music = self.deleted_musics[0]
        response = client.get(reverse('get_update_delete_music', kwargs={'id': deleted_music.id}))
        self.assertEqual(response.data['message'], 'Music not found!')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class PostMusicTest(TestCase):

    def setUp(self):
        self.all_attributes_music = {
            'title': 'Title Test',
            'artist': 'Artist Test',
            'release_date': str(datetime.date.today()),
            'duration': str(datetime.datetime.today().time()),
            'number_views': 0,
            'feat': False,
        }
        self.minimal_attributes_music = {
            'title': 'Title Test',
            'artist': 'Artist Test',
            'release_date': str(datetime.date.today()),
            'duration': str(datetime.datetime.today().time()),
        }

    def test_post_all_attributes_music(self):
        response = client.post(
            reverse('get_post_musics'),
            data=json.dumps(self.all_attributes_music),
            content_type='application/json'
        )
        music = Music.objects.get(id=1)
        serializer = MusicSerializer(music)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_post_minimal_attributes_music(self):
        response = client.post(
            reverse('get_post_musics'),
            data=json.dumps(self.minimal_attributes_music),
            content_type='application/json'
        )
        music = Music.objects.get(id=1)
        serializer = MusicSerializer(music)
        self.assertEqual(response.data['number_views'], 0)
        self.assertFalse(response.data['feat'])
        self.assertFalse(response.data['deleted'])
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_post_music_without_title_field(self):
        self.minimal_attributes_music['title'] = ''
        response = client.post(
            reverse('get_post_musics'),
            data=json.dumps(self.minimal_attributes_music),
            content_type='application/json'
        )
        self.assertEqual(response.data['message'], 'Title is required!')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_post_music_without_artist_field(self):
        self.minimal_attributes_music['artist'] = ''
        response = client.post(
            reverse('get_post_musics'),
            data=json.dumps(self.minimal_attributes_music),
            content_type='application/json'
        )
        self.assertEqual(response.data['message'], 'Artist is required!')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_post_music_without_release_date_field(self):
        self.minimal_attributes_music['release_date'] = ''
        response = client.post(
            reverse('get_post_musics'),
            data=json.dumps(self.minimal_attributes_music),
            content_type='application/json'
        )
        self.assertEqual(response.data['message'], 'Release Date is required!')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_post_music_without_duration_field(self):
        self.minimal_attributes_music['duration'] = ''
        response = client.post(
            reverse('get_post_musics'),
            data=json.dumps(self.minimal_attributes_music),
            content_type='application/json'
        )
        self.assertEqual(response.data['message'], 'Duration is required!')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class PutMusicTest(TestCase):

    def setUp(self):
        self.music = MusicFactory.create()
        self.deleted_music = MusicFactory.create(deleted=True)
        self.edited_all_attributes_music = {
            'title': f'{self.music.title} Test',
            'artist': f'{self.music.artist} Test',
            'release_date': str(datetime.date.today()),
            'duration': str(datetime.datetime.today().time()),
            'number_views': self.music.number_views + 1,
            'feat': not self.music.feat
        }
        self.edited_minimal_attributes_music = {
            'title': f'{self.music.title} Test',
            'artist': f'{self.music.artist} Test',
            'release_date': str(datetime.date.today()),
            'duration': str(datetime.datetime.today().time()),
        }

    def test_put_all_attributes_music(self):
        response = client.put(
            reverse('get_update_delete_music', kwargs={'id': self.music.id}),
            data=json.dumps(self.edited_all_attributes_music),
            content_type='application/json'
        )
        put_music = Music.objects.get(id=self.music.id)
        serializer = MusicSerializer(put_music)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_put_minimal_attributes_music(self):
        response = client.put(
            reverse('get_update_delete_music', kwargs={'id': self.music.id}),
            data=json.dumps(self.edited_minimal_attributes_music),
            content_type='application/json'
        )
        put_music = Music.objects.get(id=self.music.id)
        serializer = MusicSerializer(put_music)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_put_music_without_title_field(self):
        self.edited_minimal_attributes_music['title'] = ''
        response = client.put(
            reverse('get_update_delete_music', kwargs={'id': self.music.id}),
            data=json.dumps(self.edited_minimal_attributes_music),
            content_type='application/json'
        )
        self.assertEqual(response.data['message'], 'Title is required!')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_put_music_without_artist_field(self):
        self.edited_minimal_attributes_music['artist'] = ''
        response = client.put(
            reverse('get_update_delete_music', kwargs={'id': self.music.id}),
            data=json.dumps(self.edited_minimal_attributes_music),
            content_type='application/json'
        )
        self.assertEqual(response.data['message'], 'Artist is required!')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_put_music_without_release_date_field(self):
        self.edited_minimal_attributes_music['release_date'] = ''
        response = client.put(
            reverse('get_update_delete_music', kwargs={'id': self.music.id}),
            data=json.dumps(self.edited_minimal_attributes_music),
            content_type='application/json'
        )
        self.assertEqual(response.data['message'], 'Release Date is required!')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_music_without_duration_field(self):
        self.edited_minimal_attributes_music['duration'] = ''
        response = client.put(
            reverse('get_update_delete_music', kwargs={'id': self.music.id}),
            data=json.dumps(self.edited_minimal_attributes_music),
            content_type='application/json'
        )
        self.assertEqual(response.data['message'], 'Duration is required!')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_put_nonexistent_music(self):
        response = client.put(
            reverse('get_update_delete_music', kwargs={'id': 100}),
            data=json.dumps(self.edited_minimal_attributes_music),
            content_type='application/json'
        )
        self.assertEqual(response.data['message'], 'Music not found!')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_put_deleted_music(self):
        response = client.put(
            reverse('get_update_delete_music', kwargs={'id': self.deleted_music.id}),
            data=json.dumps(self.edited_minimal_attributes_music),
            content_type='application/json'
        )
        self.assertEqual(response.data['message'], 'Music not found!')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class DeleteMusicTest(TestCase):

    def setUp(self):
        self.music = MusicFactory.create()
        self.deleted_music = MusicFactory.create(deleted=True)

    def test_delete_music(self):
        response = client.delete(reverse('get_update_delete_music', kwargs={'id': self.music.id}))
        self.assertEqual(response.data['title'], self.music.title)
        self.assertEqual(response.data['artist'], self.music.artist)
        self.assertEqual(response.data['release_date'], str(self.music.release_date))
        self.assertEqual(response.data['duration'], str(self.music.duration))
        self.assertEqual(response.data['number_views'], self.music.number_views)
        self.assertEqual(response.data['feat'], self.music.feat)
        self.assertTrue(response.data['deleted'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_delete_nonexistent_music(self):
        response = client.delete(reverse('get_update_delete_music', kwargs={'id': 100}))
        self.assertEqual(response.data['message'], 'Music not found!')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_delete_deleted_music(self):
        response = client.delete(reverse('get_update_delete_music', kwargs={'id': self.deleted_music.id}))
        self.assertEqual(response.data['message'], 'Music not found!')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
