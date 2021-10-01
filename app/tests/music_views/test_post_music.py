import datetime
import json
from rest_framework import status
from django.test import TestCase
from django.urls import reverse
from parameterized import parameterized
from app.models import Music
from app.serializers import MusicSerializer
from app.tests.factories import create_user
from .base_tdd import (EMPTY_AUTHORIZATION_HEADER, INVALID_TOKEN_HEADER,
                       NO_TOKEN_HEADER, generate_header, get_no_bearer_header,
                       get_client)
from app.messages import (ARTIST_IS_REQUIRED, DURATION_IS_REQUIRED,
                          HEADER_AUTHORIZATION_NOT_PRESENT, INVALID_TOKEN,
                          NO_BEARER_AUTHENTICATION_SCHEME, NO_TOKEN_PROVIDED,
                          RELEASE_DATE_CANNOT_BE_FUTURE, RELEASE_DATE_IS_REQUIRED,
                          TITLE_IS_REQUIRED, WRONG_DURATION_FORMAT,
                          WRONG_RELEASE_DATE_FORMAT)

client = get_client()


class PostMusicTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.db_user1 = create_user()
        cls.header_user1 = generate_header(cls.db_user1)

    def setUp(self):

        self.all_attributes_music = {
            'title': 'Title Test',
            'artist': 'Artist Test',
            'release_date': str(datetime.date.today()),
            'duration': datetime.datetime.today().time().strftime('%H:%M:%S'),
            'number_views': 1,
            'feat': True,
        }

        self.minimal_attributes_music = {
            'title': 'Title Test',
            'artist': 'Artist Test',
            'release_date': str(datetime.date.today()),
            'duration': datetime.datetime.today().time().strftime('%H:%M:%S'),
        }

    def test_post_all_attributes_music(self):

        response = client.post(
            reverse('get_post_musics'),
            data=json.dumps(self.all_attributes_music),
            content_type='application/json',
            **self.header_user1
        )

        response_serializer = response.data

        db_music = Music.objects.get(id=response_serializer.get('id'),
                                     user=self.db_user1)
        db_music_serializer = MusicSerializer(db_music).data

        valid_title = self.all_attributes_music.get('title') == db_music_serializer.get(
            'title') == response_serializer.get('title')

        valid_artist = self.all_attributes_music.get('artist') == db_music_serializer.get(
            'artist') == response_serializer.get('artist')

        valid_release_date = self.all_attributes_music.get('release_date') == db_music_serializer.get(
            'release_date') == response_serializer.get('release_date')

        valid_duration = self.all_attributes_music.get('duration') == db_music_serializer.get(
            'duration') == response_serializer.get('duration')

        valid_number_views = self.all_attributes_music.get('number_views') == db_music_serializer.get(
            'number_views') == response_serializer.get('number_views')

        valid_feat = self.all_attributes_music.get('feat') == db_music_serializer.get(
            'feat') == response_serializer.get('feat')

        self.assertTrue(valid_title)
        self.assertTrue(valid_artist)
        self.assertTrue(valid_release_date)
        self.assertTrue(valid_duration)
        self.assertTrue(valid_number_views)
        self.assertTrue(valid_feat)
        self.assertIsNone(response_serializer.get('deleted'))
        self.assertIsNone(response_serializer.get('user'))
        self.assertIsNotNone(response_serializer.get('created_at'))
        self.assertIsNotNone(response_serializer.get('updated_at'))

        self.assertEqual(db_music_serializer.get('created_at'),
                         response_serializer.get('created_at'))

        self.assertEqual(db_music_serializer.get('updated_at'),
                         response_serializer.get('updated_at'))

        self.assertEqual(response_serializer.get('created_at'),
                         response_serializer.get('updated_at'))

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_post_minimal_attributes_music(self):

        response = client.post(
            reverse('get_post_musics'),
            data=json.dumps(self.minimal_attributes_music),
            content_type='application/json',
            **self.header_user1
        )

        response_serializer = response.data

        db_music = Music.objects.get(id=response_serializer.get('id'),
                                     user=self.db_user1)
        db_music_serializer = MusicSerializer(db_music).data

        valid_title = self.minimal_attributes_music.get('title') == db_music_serializer.get(
            'title') == response_serializer.get('title')

        valid_artist = self.minimal_attributes_music.get('artist') == db_music_serializer.get(
            'artist') == response_serializer.get('artist')

        valid_release_date = self.minimal_attributes_music.get('release_date') == db_music_serializer.get(
            'release_date') == response_serializer.get('release_date')

        valid_duration = self.minimal_attributes_music.get('duration') == db_music_serializer.get(
            'duration') == response_serializer.get('duration')

        valid_number_views = 0 == db_music_serializer.get(
            'number_views') == response_serializer.get('number_views')

        valid_feat = False == db_music_serializer.get(
            'feat') == response_serializer.get('feat')

        self.assertTrue(valid_title)
        self.assertTrue(valid_artist)
        self.assertTrue(valid_release_date)
        self.assertTrue(valid_duration)
        self.assertTrue(valid_number_views)
        self.assertTrue(valid_feat)
        self.assertIsNone(response_serializer.get('deleted'))
        self.assertIsNone(response_serializer.get('user'))
        self.assertIsNotNone(response_serializer.get('created_at'))
        self.assertIsNotNone(response_serializer.get('updated_at'))

        self.assertEqual(db_music_serializer.get('created_at'),
                         response_serializer.get('created_at'))

        self.assertEqual(db_music_serializer.get('updated_at'),
                         response_serializer.get('updated_at'))

        self.assertEqual(response_serializer.get('created_at'),
                         response_serializer.get('updated_at'))

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    @parameterized.expand([
        ('title', TITLE_IS_REQUIRED),
        ('artist', ARTIST_IS_REQUIRED),
        ('release_date', RELEASE_DATE_IS_REQUIRED),
        ('duration', DURATION_IS_REQUIRED),
    ])
    def test_post_music_without_required_fields(self, field, expected_message):

        self.minimal_attributes_music[field] = ''

        response = client.post(
            reverse('get_post_musics'),
            data=json.dumps(self.minimal_attributes_music),
            content_type='application/json',
            **self.header_user1
        )

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_post_music_with_release_date_future(self):

        tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)
        self.minimal_attributes_music['release_date'] = tomorrow.strftime(
            '%Y-%m-%d')

        response = client.post(
            reverse('get_post_musics'),
            data=json.dumps(self.minimal_attributes_music),
            content_type='application/json',
            **self.header_user1
        )

        expected_message = RELEASE_DATE_CANNOT_BE_FUTURE

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_post_music_wrong_release_date_format(self):

        self.minimal_attributes_music['release_date'] = self.minimal_attributes_music.get(
            'release_date').replace('-', '/')

        response = client.post(
            reverse('get_post_musics'),
            data=json.dumps(self.minimal_attributes_music),
            content_type='application/json',
            **self.header_user1
        )

        expected_message = WRONG_RELEASE_DATE_FORMAT

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_post_music_wrong_release_date_format(self):

        self.minimal_attributes_music['duration'] = self.minimal_attributes_music.get(
            'duration').replace(':', '/')

        response = client.post(
            reverse('get_post_musics'),
            data=json.dumps(self.minimal_attributes_music),
            content_type='application/json',
            **self.header_user1
        )

        self.assertEqual(WRONG_DURATION_FORMAT, response.data.get('message'))
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    @parameterized.expand([
        (INVALID_TOKEN_HEADER, INVALID_TOKEN),
        (EMPTY_AUTHORIZATION_HEADER, HEADER_AUTHORIZATION_NOT_PRESENT),
        (NO_TOKEN_HEADER, NO_TOKEN_PROVIDED),
    ])
    def test_post_music_with_inappropriate_tokens(self, header, expected_message):

        response = client.post(
            reverse('get_post_musics'),
            data=json.dumps(self.minimal_attributes_music),
            content_type='application/json',
            **header
        )

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_post_music_without_authorization_header(self):

        response = client.post(
            reverse('get_post_musics'),
            data=json.dumps(self.minimal_attributes_music),
            content_type='application/json'
        )

        expected_message = HEADER_AUTHORIZATION_NOT_PRESENT

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_music_without_bearer_authentication_scheme(self):

        response = client.post(
            reverse('get_post_musics'),
            data=json.dumps(self.minimal_attributes_music),
            content_type='application/json',
            **get_no_bearer_header(self.header_user1)
        )

        expected_message = NO_BEARER_AUTHENTICATION_SCHEME

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
