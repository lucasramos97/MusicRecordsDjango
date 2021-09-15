import json
import datetime
from rest_framework import status
from django.test import TestCase, Client
from django.urls import reverse
from app.models import Music, User
from app.serializers import MusicSerializer
from app.tests.factories import MusicFactory

EMPTY_AUTHORIZATION_MESSAGE = 'Header Authorization not present!'
NO_BEARER_SCHEME_MESSAGE = 'No Bearer HTTP authentication scheme!'


client = Client()


def create_users(user_id=1):

    user_dict = {
        'username': 'user{}'.format(user_id),
        'email': 'user{}@email.com'.format(user_id),
        'password': 'test{}'.format(user_id)
    }

    user_db = User.objects.create_user(
        username=user_dict['username'],
        email=user_dict['email'],
        password=user_dict['password']
    )

    user_response = client.post(
        reverse('login'),
        data=json.dumps(user_dict),
        content_type='application/json'
    )

    user_header = {
        'HTTP_AUTHORIZATION': 'Bearer {}'.format(user_response.data['token'])
    }

    return user_db, user_header


def init_tests(cls):

    cls.user1_db, cls.user1_header = create_users()
    cls.user2_db, cls.user2_header = create_users(2)
    cls.invalid_token_header = {
        'HTTP_AUTHORIZATION': 'Bearer 123'
    }
    cls.empty_authorization_header = {
        'HTTP_AUTHORIZATION': ''
    }
    cls.no_bearer_header = {
        'HTTP_AUTHORIZATION': 'Token {}'.format(cls.user1_header['HTTP_AUTHORIZATION'].split('Bearer ')[1])
    }
    cls.no_token_header = {
        'HTTP_AUTHORIZATION': 'Bearer '
    }


class GetAllMusicsTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        init_tests(cls)
        MusicFactory.create_batch(10, user=cls.user1_db)
        MusicFactory.create_batch(10, user=cls.user2_db)
        MusicFactory.create(deleted=True, user=cls.user1_db)

    def test_get_all_musics_with_default_query_params(self):

        response = client.get(
            reverse('get_post_musics'),
            **self.user1_header
        )

        user1_musics = Music.objects.filter(deleted=False, user=self.user1_db)
        serializer = MusicSerializer(user1_musics[:5], many=True)

        self.assertEqual(response.data['content'], serializer.data)
        self.assertEqual(len(response.data['content']), 5)
        self.assertEqual(response.data['total'], len(user1_musics))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_musics_with_explicit_query_params(self):

        response = client.get(
            reverse('get_post_musics'),
            {'page': 2, 'size': 4},
            **self.user1_header
        )

        user1_musics = Music.objects.filter(deleted=False, user=self.user1_db)
        serializer = MusicSerializer(user1_musics[4:8], many=True)

        self.assertEqual(response.data['content'], serializer.data)
        self.assertEqual(len(response.data['content']), 4)
        self.assertEqual(response.data['total'], len(user1_musics))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_musics_with_invalid_token(self):

        response = client.get(
            reverse('get_post_musics'),
            **self.invalid_token_header
        )

        self.assertEqual(response.data['message'], 'Invalid token!')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_all_musics_without_authorization_header(self):

        response = client.get(
            reverse('get_post_musics')
        )

        self.assertEqual(response.data['message'], EMPTY_AUTHORIZATION_MESSAGE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_all_musics_empty_authorization_header(self):

        response = client.get(reverse('get_post_musics'),
                              **self.empty_authorization_header)

        self.assertEqual(response.data['message'], EMPTY_AUTHORIZATION_MESSAGE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_all_musics_without_bearer_authentication_scheme(self):

        response = client.get(
            reverse('get_post_musics'),
            **self.no_bearer_header
        )

        self.assertEqual(response.data['message'], NO_BEARER_SCHEME_MESSAGE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_all_musics_with_no_token_header(self):

        response = client.get(
            reverse('get_post_musics'),
            **self.no_token_header
        )

        self.assertEqual(response.data['message'], 'No token provided!')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class GetMusicByIdTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        init_tests(cls)
        cls.music = MusicFactory.create(user=cls.user1_db)
        cls.deleted_music = MusicFactory.create(
            deleted=True, user=cls.user1_db)

    def test_get_music_by_id(self):

        response = client.get(
            reverse('get_update_delete_music', kwargs={'id': self.music.id}),
            **self.user1_header
        )

        serializer = MusicSerializer(self.music)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_nonexistent_music_by_id(self):

        response = client.get(
            reverse('get_update_delete_music', kwargs={'id': 100}),
            **self.user1_header
        )

        self.assertEqual(response.data['message'], 'Music not found!')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_deleted_music_by_id(self):

        response = client.get(
            reverse(
                'get_update_delete_music',
                kwargs={'id': self.deleted_music.id}
            ),
            **self.user1_header
        )

        self.assertEqual(response.data['message'], 'Music not found!')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_nonexistent_music_by_user(self):

        response = client.get(
            reverse('get_update_delete_music', kwargs={'id': self.music.id}),
            **self.user2_header
        )

        self.assertEqual(response.data['message'], 'Music not found!')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_music_by_id_with_invalid_token(self):

        response = client.get(
            reverse('get_update_delete_music', kwargs={'id': self.music.id}),
            **self.invalid_token_header
        )

        self.assertEqual(response.data['message'], 'Invalid token!')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_music_by_id_without_authorization_header(self):

        response = client.get(
            reverse('get_update_delete_music', kwargs={'id': self.music.id})
        )

        self.assertEqual(response.data['message'], EMPTY_AUTHORIZATION_MESSAGE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_music_by_id_empty_authorization_header(self):

        response = client.get(
            reverse('get_update_delete_music', kwargs={'id': self.music.id}),
            **self.empty_authorization_header
        )

        self.assertEqual(response.data['message'], EMPTY_AUTHORIZATION_MESSAGE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_music_by_id_without_bearer_authentication_scheme(self):

        response = client.get(
            reverse('get_update_delete_music', kwargs={'id': self.music.id}),
            **self.no_bearer_header
        )

        self.assertEqual(response.data['message'], NO_BEARER_SCHEME_MESSAGE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_music_by_id_with_no_token_header(self):

        response = client.get(
            reverse('get_update_delete_music', kwargs={'id': self.music.id}),
            **self.no_token_header
        )

        self.assertEqual(response.data['message'], 'No token provided!')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PostMusicTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        init_tests(cls)
        cls.all_attributes_music = {
            'title': 'Title Test',
            'artist': 'Artist Test',
            'release_date': str(datetime.date.today()),
            'duration': str(datetime.datetime.today().time()),
            'number_views': 0,
            'feat': False,
        }
        cls.minimal_attributes_music = {
            'title': 'Title Test',
            'artist': 'Artist Test',
            'release_date': str(datetime.date.today()),
            'duration': str(datetime.datetime.today().time()),
        }

    def test_post_all_attributes_music(self):

        response = client.post(
            reverse('get_post_musics'),
            data=json.dumps(self.all_attributes_music),
            content_type='application/json',
            **self.user1_header
        )

        music = Music.objects.get(id=response.data['id'])
        serializer = MusicSerializer(music)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_minimal_attributes_music(self):

        response = client.post(
            reverse('get_post_musics'),
            data=json.dumps(self.minimal_attributes_music),
            content_type='application/json',
            **self.user1_header
        )

        music = Music.objects.get(id=response.data['id'])
        serializer = MusicSerializer(music)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_music_without_title_field(self):

        self.minimal_attributes_music['title'] = ''

        response = client.post(
            reverse('get_post_musics'),
            data=json.dumps(self.minimal_attributes_music),
            content_type='application/json',
            **self.user1_header
        )

        self.assertEqual(response.data['message'], 'Title is required!')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_music_without_artist_field(self):

        self.minimal_attributes_music['artist'] = ''

        response = client.post(
            reverse('get_post_musics'),
            data=json.dumps(self.minimal_attributes_music),
            content_type='application/json',
            **self.user1_header
        )

        self.assertEqual(response.data['message'], 'Artist is required!')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_music_without_release_date_field(self):

        self.minimal_attributes_music['release_date'] = ''

        response = client.post(
            reverse('get_post_musics'),
            data=json.dumps(self.minimal_attributes_music),
            content_type='application/json',
            **self.user1_header
        )

        self.assertEqual(response.data['message'], 'Release Date is required!')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_music_without_duration_field(self):

        self.minimal_attributes_music['duration'] = ''

        response = client.post(
            reverse('get_post_musics'),
            data=json.dumps(self.minimal_attributes_music),
            content_type='application/json',
            **self.user1_header
        )

        self.assertEqual(response.data['message'], 'Duration is required!')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_music_with_invalid_token(self):

        response = client.post(
            reverse('get_post_musics'),
            data=json.dumps(self.minimal_attributes_music),
            content_type='application/json',
            **self.invalid_token_header
        )

        self.assertEqual(response.data['message'], 'Invalid token!')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_music_without_authorization_header(self):

        response = client.post(
            reverse('get_post_musics'),
            data=json.dumps(self.minimal_attributes_music),
            content_type='application/json'
        )

        self.assertEqual(response.data['message'], EMPTY_AUTHORIZATION_MESSAGE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_music_empty_authorization_header(self):

        response = client.post(
            reverse('get_post_musics'),
            data=json.dumps(self.minimal_attributes_music),
            content_type='application/json',
            **self.empty_authorization_header
        )

        self.assertEqual(response.data['message'], EMPTY_AUTHORIZATION_MESSAGE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_music_without_bearer_authentication_scheme(self):

        response = client.post(
            reverse('get_post_musics'),
            data=json.dumps(self.minimal_attributes_music),
            content_type='application/json',
            **self.no_bearer_header
        )

        self.assertEqual(response.data['message'], NO_BEARER_SCHEME_MESSAGE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_music_with_no_token_header(self):

        response = client.post(
            reverse('get_post_musics'),
            data=json.dumps(self.minimal_attributes_music),
            content_type='application/json',
            **self.no_token_header
        )

        self.assertEqual(response.data['message'], 'No token provided!')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PutMusicTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        init_tests(cls)
        cls.music = MusicFactory.create(user=cls.user1_db)
        cls.deleted_music = MusicFactory.create(
            deleted=True, user=cls.user1_db)
        cls.edited_all_attributes_music = {
            'title': '{} Test'.format(cls.music.title),
            'artist': '{} Test'.format(cls.music.artist),
            'release_date': str(datetime.date.today()),
            'duration': str(datetime.datetime.today().time()),
            'number_views': cls.music.number_views + 1,
            'feat': not cls.music.feat
        }
        cls.edited_minimal_attributes_music = {
            'title': '{} Test'.format(cls.music.title),
            'artist': '{} Test'.format(cls.music.artist),
            'release_date': str(datetime.date.today()),
            'duration': str(datetime.datetime.today().time()),
        }

    def test_put_all_attributes_music(self):
        response = client.put(
            reverse('get_update_delete_music', kwargs={'id': self.music.id}),
            data=json.dumps(self.edited_all_attributes_music),
            content_type='application/json',
            **self.user1_header
        )

        put_music = Music.objects.get(id=self.music.id)
        serializer = MusicSerializer(put_music)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put_minimal_attributes_music(self):

        response = client.put(
            reverse('get_update_delete_music', kwargs={'id': self.music.id}),
            data=json.dumps(self.edited_minimal_attributes_music),
            content_type='application/json',
            **self.user1_header
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
            content_type='application/json',
            **self.user1_header
        )

        self.assertEqual(response.data['message'], 'Title is required!')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_music_without_artist_field(self):

        self.edited_minimal_attributes_music['artist'] = ''

        response = client.put(
            reverse('get_update_delete_music', kwargs={'id': self.music.id}),
            data=json.dumps(self.edited_minimal_attributes_music),
            content_type='application/json',
            **self.user1_header
        )

        self.assertEqual(response.data['message'], 'Artist is required!')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_music_without_release_date_field(self):

        self.edited_minimal_attributes_music['release_date'] = ''

        response = client.put(
            reverse('get_update_delete_music', kwargs={'id': self.music.id}),
            data=json.dumps(self.edited_minimal_attributes_music),
            content_type='application/json',
            **self.user1_header
        )

        self.assertEqual(response.data['message'], 'Release Date is required!')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_music_without_duration_field(self):

        self.edited_minimal_attributes_music['duration'] = ''

        response = client.put(
            reverse('get_update_delete_music', kwargs={'id': self.music.id}),
            data=json.dumps(self.edited_minimal_attributes_music),
            content_type='application/json',
            **self.user1_header
        )

        self.assertEqual(response.data['message'], 'Duration is required!')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_nonexistent_music_by_id(self):

        response = client.put(
            reverse('get_update_delete_music', kwargs={'id': 100}),
            data=json.dumps(self.edited_minimal_attributes_music),
            content_type='application/json',
            **self.user1_header
        )

        self.assertEqual(response.data['message'], 'Music not found!')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_deleted_music(self):

        response = client.put(
            reverse(
                'get_update_delete_music',
                kwargs={'id': self.deleted_music.id}
            ),
            data=json.dumps(self.edited_minimal_attributes_music),
            content_type='application/json',
            **self.user1_header
        )

        self.assertEqual(response.data['message'], 'Music not found!')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_nonexistent_music_by_user(self):

        response = client.put(
            reverse('get_update_delete_music', kwargs={'id': self.music.id}),
            data=json.dumps(self.edited_minimal_attributes_music),
            content_type='application/json',
            **self.user2_header
        )

        self.assertEqual(response.data['message'], 'Music not found!')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_music_with_invalid_token(self):

        response = client.put(
            reverse('get_update_delete_music', kwargs={'id': self.music.id}),
            data=json.dumps(self.edited_minimal_attributes_music),
            content_type='application/json',
            **self.invalid_token_header
        )

        self.assertEqual(response.data['message'], 'Invalid token!')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_music_without_authorization_header(self):

        response = client.put(
            reverse('get_update_delete_music', kwargs={'id': self.music.id}),
            data=json.dumps(self.edited_minimal_attributes_music),
            content_type='application/json'
        )

        self.assertEqual(response.data['message'], EMPTY_AUTHORIZATION_MESSAGE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_music_empty_authorization_header(self):

        response = client.put(
            reverse('get_update_delete_music', kwargs={'id': self.music.id}),
            data=json.dumps(self.edited_minimal_attributes_music),
            content_type='application/json',
            **self.empty_authorization_header
        )

        self.assertEqual(response.data['message'], EMPTY_AUTHORIZATION_MESSAGE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_music_without_bearer_authentication_scheme(self):

        response = client.put(
            reverse('get_update_delete_music', kwargs={'id': self.music.id}),
            data=json.dumps(self.edited_minimal_attributes_music),
            content_type='application/json',
            **self.no_bearer_header
        )

        self.assertEqual(response.data['message'], NO_BEARER_SCHEME_MESSAGE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_music_with_no_token_header(self):

        response = client.put(
            reverse('get_update_delete_music', kwargs={'id': self.music.id}),
            data=json.dumps(self.edited_minimal_attributes_music),
            content_type='application/json',
            **self.no_token_header
        )

        self.assertEqual(response.data['message'], 'No token provided!')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class DeleteMusicTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        init_tests(cls)
        cls.music = MusicFactory.create(user=cls.user1_db)
        cls.deleted_music = MusicFactory.create(
            deleted=True, user=cls.user1_db)

    def test_delete_music(self):

        response = client.delete(
            reverse('get_update_delete_music', kwargs={'id': self.music.id}),
            **self.user1_header
        )

        deleted_music = Music.objects.get(id=self.music.id)
        serializer = MusicSerializer(deleted_music)

        keys = ['id', 'title', 'artist', 'release_date',
                'duration', 'number_views', 'feat', 'created_at', 'updated_at']

        equal_values_response_music = {x: response.data[x] for x in keys}
        equal_values_db_music = {x: serializer.data[x] for x in keys}

        self.assertEqual(equal_values_response_music, equal_values_db_music)
        self.assertTrue(deleted_music.deleted)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_nonexistent_music_by_id(self):

        response = client.delete(
            reverse('get_update_delete_music', kwargs={'id': 100}),
            **self.user1_header
        )

        self.assertEqual(response.data['message'], 'Music not found!')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_deleted_music(self):

        response = client.delete(
            reverse(
                'get_update_delete_music',
                kwargs={'id': self.deleted_music.id}
            ),
            **self.user1_header
        )

        self.assertEqual(response.data['message'], 'Music not found!')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_nonexistent_music_by_user(self):

        response = client.delete(
            reverse('get_update_delete_music', kwargs={'id': 100}),
            **self.user2_header
        )

        self.assertEqual(response.data['message'], 'Music not found!')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_music_with_invalid_token(self):

        response = client.delete(
            reverse('get_update_delete_music', kwargs={'id': self.music.id}),
            **self.invalid_token_header
        )

        self.assertEqual(response.data['message'], 'Invalid token!')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_music_without_authorization_header(self):

        response = client.delete(
            reverse('get_update_delete_music', kwargs={'id': self.music.id})
        )

        self.assertEqual(response.data['message'], EMPTY_AUTHORIZATION_MESSAGE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_music_empty_authorization_header(self):

        response = client.delete(
            reverse('get_update_delete_music', kwargs={'id': self.music.id}),
            **self.empty_authorization_header
        )

        self.assertEqual(response.data['message'], EMPTY_AUTHORIZATION_MESSAGE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_music_without_bearer_authentication_scheme(self):

        response = client.delete(
            reverse('get_update_delete_music', kwargs={'id': self.music.id}),
            **self.no_bearer_header
        )

        self.assertEqual(response.data['message'], NO_BEARER_SCHEME_MESSAGE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_music_with_no_token_header(self):

        response = client.delete(
            reverse('get_update_delete_music', kwargs={'id': self.music.id}),
            **self.no_token_header
        )

        self.assertEqual(response.data['message'], 'No token provided!')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CountDeletedMusicsTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        init_tests(cls)
        MusicFactory.create_batch(10, deleted=True, user=cls.user1_db)
        MusicFactory.create(deleted=True, user=cls.user2_db)
        MusicFactory.create(user=cls.user1_db)

    def test_count_deleted_music(self):

        response = client.get(
            reverse('count_deleted_musics'),
            **self.user1_header
        )

        self.assertEqual(response.data, 10)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_count_deleted_music_with_invalid_token(self):

        response = client.get(
            reverse('count_deleted_musics'),
            **self.invalid_token_header
        )

        self.assertEqual(response.data['message'], 'Invalid token!')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_count_deleted_music_without_authorization_header(self):

        response = client.get(
            reverse('count_deleted_musics')
        )

        self.assertEqual(response.data['message'], EMPTY_AUTHORIZATION_MESSAGE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_count_deleted_music_empty_authorization_header(self):

        response = client.get(
            reverse('count_deleted_musics'),
            **self.empty_authorization_header
        )

        self.assertEqual(response.data['message'], EMPTY_AUTHORIZATION_MESSAGE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_count_deleted_music_without_bearer_authentication_scheme(self):

        response = client.get(
            reverse('count_deleted_musics'),
            **self.no_bearer_header
        )

        self.assertEqual(response.data['message'], NO_BEARER_SCHEME_MESSAGE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_count_deleted_music_with_no_token_header(self):

        response = client.get(
            reverse('count_deleted_musics'),
            **self.no_token_header
        )

        self.assertEqual(response.data['message'], 'No token provided!')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class GetAllDeletedMusicsTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        init_tests(cls)
        MusicFactory.create_batch(10, deleted=True, user=cls.user1_db)
        MusicFactory.create_batch(10, deleted=True, user=cls.user2_db)
        MusicFactory.create(user=cls.user1_db)

    def test_get_all_deleted_musics_with_default_query_params(self):

        response = client.get(
            reverse('get_deleted_musics'),
            **self.user1_header
        )

        user1_deleted_musics = Music.objects.filter(
            deleted=True, user=self.user1_db)

        serializer = MusicSerializer(user1_deleted_musics[:5], many=True)

        self.assertEqual(response.data['content'], serializer.data)
        self.assertEqual(len(response.data['content']), 5)
        self.assertEqual(response.data['total'], len(user1_deleted_musics))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_deleted_musics_with_explicit_query_params(self):

        response = client.get(
            reverse('get_deleted_musics'), {'page': 2, 'size': 4},
            **self.user1_header
        )

        user1_deleted_musics = Music.objects.filter(
            deleted=True, user=self.user1_db)

        serializer = MusicSerializer(user1_deleted_musics[4:8], many=True)

        self.assertEqual(response.data['content'], serializer.data)
        self.assertEqual(len(response.data['content']), 4)
        self.assertEqual(response.data['total'], len(user1_deleted_musics))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_deleted_musics_with_invalid_token(self):

        response = client.get(
            reverse('get_deleted_musics'),
            **self.invalid_token_header
        )

        self.assertEqual(response.data['message'], 'Invalid token!')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_all_deleted_musics_without_authorization_header(self):

        response = client.get(
            reverse('get_deleted_musics')
        )

        self.assertEqual(response.data['message'], EMPTY_AUTHORIZATION_MESSAGE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_all_deleted_musics_empty_authorization_header(self):

        response = client.get(
            reverse('get_deleted_musics'),
            **self.empty_authorization_header
        )

        self.assertEqual(response.data['message'], EMPTY_AUTHORIZATION_MESSAGE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_all_deleted_musics_without_bearer_authentication_scheme(self):

        response = client.get(
            reverse('get_deleted_musics'),
            **self.no_bearer_header
        )

        self.assertEqual(response.data['message'], NO_BEARER_SCHEME_MESSAGE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_all_deleted_musics_with_no_token_header(self):

        response = client.get(
            reverse('get_deleted_musics'),
            **self.no_token_header
        )

        self.assertEqual(response.data['message'], 'No token provided!')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RestoreDeletedMusicsTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        init_tests(cls)
        cls.user1_deleted_musics = MusicFactory.create_batch(
            10, deleted=True, user=cls.user1_db)
        cls.user2_deleted_musics = MusicFactory.create_batch(
            10, deleted=True, user=cls.user2_db)
        cls.serializer = MusicSerializer(
            cls.user1_deleted_musics[:4], many=True)

    def test_restore_deleted_musics(self):

        response = client.post(
            reverse('restore_deleted_musics'),
            data=json.dumps(self.serializer.data),
            content_type='application/json',
            **self.user1_header
        )

        user1_count_deleted_musics = Music.objects.filter(
            deleted=True, user=self.user1_db).count()

        user2_count_deleted_musics = Music.objects.filter(
            deleted=True, user=self.user2_db).count()

        self.assertEqual(response.data, 4)
        self.assertEqual(user1_count_deleted_musics, 6)
        self.assertEqual(user2_count_deleted_musics, 10)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_restore_deleted_musics_with_invalid_token(self):

        response = client.post(
            reverse('restore_deleted_musics'),
            data=json.dumps(self.serializer.data),
            content_type='application/json',
            **self.invalid_token_header
        )

        self.assertEqual(response.data['message'], 'Invalid token!')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_restore_deleted_musics_without_authorization_header(self):

        response = client.post(
            reverse('restore_deleted_musics'),
            data=json.dumps(self.serializer.data),
            content_type='application/json'
        )

        self.assertEqual(response.data['message'], EMPTY_AUTHORIZATION_MESSAGE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_restore_deleted_musics_empty_authorization_header(self):

        response = client.post(
            reverse('restore_deleted_musics'),
            data=json.dumps(self.serializer.data),
            content_type='application/json',
            **self.empty_authorization_header
        )

        self.assertEqual(response.data['message'], EMPTY_AUTHORIZATION_MESSAGE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_restore_deleted_musics_without_bearer_authentication_scheme(self):

        response = client.post(
            reverse('restore_deleted_musics'),
            data=json.dumps(self.serializer.data),
            content_type='application/json',
            **self.no_bearer_header
        )

        self.assertEqual(response.data['message'], NO_BEARER_SCHEME_MESSAGE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_restore_deleted_musics_with_no_token_header(self):

        response = client.post(
            reverse('restore_deleted_musics'),
            data=json.dumps(self.serializer.data),
            content_type='application/json',
            **self.no_token_header
        )

        self.assertEqual(response.data['message'], 'No token provided!')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class EmptyListTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        init_tests(cls)
        MusicFactory.create_batch(10, deleted=True, user=cls.user1_db)
        MusicFactory.create_batch(10, deleted=True, user=cls.user2_db)
        MusicFactory.create(user=cls.user1_db)

    def test_empty_list(self):

        response = client.delete(
            reverse('empty_list'),
            **self.user1_header
        )

        user1_count_all_musics = Music.objects.filter(
            user=self.user1_db).count()
        user2_count_all_musics = Music.objects.filter(
            user=self.user2_db).count()

        self.assertEqual(user1_count_all_musics, 1)
        self.assertEqual(user2_count_all_musics, 10)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_empty_list_with_invalid_token(self):

        response = client.delete(
            reverse('empty_list'),
            **self.invalid_token_header
        )

        self.assertEqual(response.data['message'], 'Invalid token!')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_empty_list_without_authorization_header(self):

        response = client.delete(
            reverse('empty_list')
        )

        self.assertEqual(response.data['message'], EMPTY_AUTHORIZATION_MESSAGE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_empty_list_empty_authorization_header(self):

        response = client.delete(
            reverse('empty_list'),
            **self.empty_authorization_header
        )

        self.assertEqual(response.data['message'], EMPTY_AUTHORIZATION_MESSAGE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_empty_list_without_bearer_authentication_scheme(self):

        response = client.delete(
            reverse('empty_list'),
            **self.no_bearer_header
        )

        self.assertEqual(response.data['message'], NO_BEARER_SCHEME_MESSAGE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_empty_list_with_no_token_header(self):

        response = client.delete(
            reverse('empty_list'),
            **self.no_token_header
        )

        self.assertEqual(response.data['message'], 'No token provided!')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class DefinitiveDeleteMusicTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        init_tests(cls)
        cls.deleted_music = MusicFactory.create(
            deleted=True, user=cls.user1_db)
        cls.music = MusicFactory.create(user=cls.user1_db)

    def test_definitive_delete_music(self):

        response = client.delete(
            reverse(
                'definitive_delete_music',
                kwargs={'id': self.deleted_music.id}
            ),
            **self.user1_header
        )

        count_deleted_musics = Music.objects.filter(
            deleted=True, user=self.user1_db).count()

        self.assertEqual(count_deleted_musics, 0)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_definitive_delete_nonexistent_music(self):

        response = client.delete(
            reverse('definitive_delete_music', kwargs={'id': 100}),
            **self.user1_header
        )

        self.assertEqual(response.data['message'], 'Music not found!')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_definitive_delete_not_deleted_music(self):

        response = client.delete(
            reverse('definitive_delete_music', kwargs={'id': self.music.id}),
            **self.user1_header
        )

        self.assertEqual(response.data['message'], 'Music not found!')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_definitive_delete_music_defer_by_user(self):

        response = client.delete(
            reverse(
                'definitive_delete_music',
                kwargs={'id': self.deleted_music.id}
            ),
            **self.user2_header
        )

        self.assertEqual(response.data['message'], 'Music not found!')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_definitive_delete_music_with_invalid_token(self):

        response = client.delete(
            reverse(
                'definitive_delete_music',
                kwargs={'id': self.deleted_music.id}
            ),
            **self.invalid_token_header
        )

        self.assertEqual(response.data['message'], 'Invalid token!')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_definitive_delete_music_without_authorization_header(self):

        response = client.delete(
            reverse(
                'definitive_delete_music',
                kwargs={'id': self.deleted_music.id}
            )
        )

        self.assertEqual(response.data['message'], EMPTY_AUTHORIZATION_MESSAGE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_definitive_delete_music_empty_authorization_header(self):

        response = client.delete(
            reverse(
                'definitive_delete_music',
                kwargs={'id': self.deleted_music.id}
            ),
            **self.empty_authorization_header
        )

        self.assertEqual(response.data['message'], EMPTY_AUTHORIZATION_MESSAGE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_definitive_delete_music_without_bearer_authentication_scheme(self):

        response = client.delete(
            reverse(
                'definitive_delete_music',
                kwargs={'id': self.deleted_music.id}
            ),
            **self.no_bearer_header
        )

        self.assertEqual(response.data['message'], NO_BEARER_SCHEME_MESSAGE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_definitive_delete_music_with_no_token_header(self):

        response = client.delete(
            reverse(
                'definitive_delete_music',
                kwargs={'id': self.deleted_music.id}
            ),
            **self.no_token_header
        )

        self.assertEqual(response.data['message'], 'No token provided!')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
