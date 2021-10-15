import datetime
import json
from rest_framework import status
from django.test import TestCase
from django.urls import reverse
from parameterized import parameterized
from app import messages
from app.models import Music
from app.serializers import MusicSerializer
from app.tests import base_tdd
from app.tests.factories import MusicFactory, create_user

client = base_tdd.get_client()


class PutMusicTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.db_user1 = create_user()
        cls.header_user1 = base_tdd.generate_header(cls.db_user1)
        cls.header_user2 = base_tdd.generate_header(create_user('2'))

        cls.music = MusicFactory.create(user=cls.db_user1)
        cls.deleted_music = MusicFactory.create(deleted=True,
                                                user=cls.db_user1)

    def setUp(self):

        self.all_attributes_music = {
            'title': '{} Test'.format(self.music.title),
            'artist': '{} Test'.format(self.music.artist),
            'release_date': str(datetime.date.today()),
            'duration': datetime.datetime.today().time().strftime('%H:%M:%S'),
            'number_views': self.music.number_views + 1,
            'feat': not self.music.feat,
        }

        self.minimal_attributes_music = {
            'title': '{} Test'.format(self.music.title),
            'artist': '{} Test'.format(self.music.artist),
            'release_date': str(datetime.date.today()),
            'duration': datetime.datetime.today().time().strftime('%H:%M:%S'),
        }

    def test_put_all_attributes_music(self):

        response = client.put(
            reverse(
                'get_update_delete_music',
                kwargs={
                    'id': self.music.id
                }
            ),
            data=json.dumps(self.all_attributes_music),
            content_type='application/json',
            **self.header_user1
        )

        response_serializer = response.data

        music_serializer = MusicSerializer(self.music).data

        db_music = Music.objects.get(id=self.music.id,
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

        valid_created_at = music_serializer.get('created_at') == db_music_serializer.get(
            'created_at') == response_serializer.get('created_at')

        self.assertEqual(music_serializer.get('id'),
                         response_serializer.get('id'))

        self.assertTrue(valid_title)
        self.assertNotEqual(music_serializer.get('title'),
                            response_serializer.get('title'))

        self.assertTrue(valid_artist)
        self.assertNotEqual(music_serializer.get('artist'),
                            response_serializer.get('artist'))

        self.assertIsNotNone(base_tdd.match_date(
            response_serializer.get('release_date')))

        self.assertTrue(valid_release_date)
        self.assertNotEqual(music_serializer.get('release_date'),
                            response_serializer.get('release_date'))

        self.assertIsNotNone(base_tdd.match_time(
            response_serializer.get('duration')))

        self.assertTrue(valid_duration)
        self.assertNotEqual(music_serializer.get('duration'),
                            response_serializer.get('duration'))

        self.assertTrue(valid_number_views)
        self.assertNotEqual(music_serializer.get('number_views'),
                            response_serializer.get('number_views'))

        self.assertTrue(valid_feat)
        self.assertNotEqual(music_serializer.get('feat'),
                            response_serializer.get('feat'))

        self.assertIsNone(response_serializer.get('deleted'))
        self.assertIsNone(response_serializer.get('user'))
        self.assertIsNotNone(base_tdd.match_date_time(
            response_serializer.get('created_at')))

        self.assertIsNotNone(base_tdd.match_date_time(
            response_serializer.get('updated_at')))

        self.assertTrue(valid_created_at)
        self.assertEqual(db_music_serializer.get('updated_at'),
                         response_serializer.get('updated_at'))

        self.assertNotEqual(music_serializer.get('updated_at'),
                            response_serializer.get('updated_at'))

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_put_minimal_attributes_music(self):

        response = client.put(
            reverse(
                'get_update_delete_music',
                kwargs={
                    'id': self.music.id
                }
            ),
            data=json.dumps(self.minimal_attributes_music),
            content_type='application/json',
            **self.header_user1
        )

        response_serializer = response.data

        music_serializer = MusicSerializer(self.music).data

        db_music = Music.objects.get(id=self.music.id,
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

        valid_number_views = music_serializer.get('number_views') == db_music_serializer.get(
            'number_views') == response_serializer.get('number_views')

        valid_feat = music_serializer.get('feat') == db_music_serializer.get(
            'feat') == response_serializer.get('feat')

        valid_created_at = music_serializer.get('created_at') == db_music_serializer.get(
            'created_at') == response_serializer.get('created_at')

        self.assertEqual(music_serializer.get('id'),
                         response_serializer.get('id'))

        self.assertTrue(valid_title)
        self.assertNotEqual(music_serializer.get('title'),
                            response_serializer.get('title'))

        self.assertTrue(valid_artist)
        self.assertNotEqual(music_serializer.get('artist'),
                            response_serializer.get('artist'))

        self.assertIsNotNone(base_tdd.match_date(
            response_serializer.get('release_date')))

        self.assertTrue(valid_release_date)
        self.assertNotEqual(music_serializer.get('release_date'),
                            response_serializer.get('release_date'))

        self.assertIsNotNone(base_tdd.match_time(
            response_serializer.get('duration')))

        self.assertTrue(valid_duration)
        self.assertNotEqual(music_serializer.get('duration'),
                            response_serializer.get('duration'))

        self.assertTrue(valid_number_views)
        self.assertTrue(valid_feat)
        self.assertIsNone(response_serializer.get('deleted'))
        self.assertIsNone(response_serializer.get('user'))
        self.assertIsNotNone(base_tdd.match_date_time(
            response_serializer.get('created_at')))

        self.assertIsNotNone(base_tdd.match_date_time(
            response_serializer.get('updated_at')))

        self.assertTrue(valid_created_at)
        self.assertEqual(db_music_serializer.get('updated_at'),
                         response_serializer.get('updated_at'))

        self.assertNotEqual(music_serializer.get('updated_at'),
                            response_serializer.get('updated_at'))

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_put_nonexistent_music_by_id(self):

        response = client.put(
            reverse(
                'get_update_delete_music',
                kwargs={
                    'id': 100
                }
            ),
            data=json.dumps(self.minimal_attributes_music),
            content_type='application/json',
            **self.header_user1
        )

        expected_message = messages.MUSIC_NOT_FOUND

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_put_deleted_music(self):

        response = client.put(
            reverse(
                'get_update_delete_music',
                kwargs={
                    'id': self.deleted_music.id
                }
            ),
            data=json.dumps(self.minimal_attributes_music),
            content_type='application/json',
            **self.header_user1
        )

        expected_message = messages.MUSIC_NOT_FOUND

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_put_nonexistent_music_by_user(self):

        response = client.put(
            reverse(
                'get_update_delete_music',
                kwargs={
                    'id': self.music.id
                }
            ),
            data=json.dumps(self.minimal_attributes_music),
            content_type='application/json',
            **self.header_user2
        )

        expected_message = messages.MUSIC_NOT_FOUND

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    @parameterized.expand([
        ('title', messages.TITLE_IS_REQUIRED),
        ('artist', messages.ARTIST_IS_REQUIRED),
        ('release_date', messages.RELEASE_DATE_IS_REQUIRED),
        ('duration', messages.DURATION_IS_REQUIRED),
    ])
    def test_put_music_without_required_fields(self, field, expected_message):

        self.minimal_attributes_music[field] = ''

        response = client.put(
            reverse(
                'get_update_delete_music',
                kwargs={
                    'id': self.music.id
                }
            ),
            data=json.dumps(self.minimal_attributes_music),
            content_type='application/json',
            **self.header_user1
        )

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_put_music_with_release_date_future(self):

        tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)
        self.minimal_attributes_music['release_date'] = tomorrow.strftime(
            '%Y-%m-%d')

        response = client.put(
            reverse(
                'get_update_delete_music',
                kwargs={
                    'id': self.music.id
                }
            ),
            data=json.dumps(self.minimal_attributes_music),
            content_type='application/json',
            **self.header_user1
        )

        expected_message = messages.RELEASE_DATE_CANNOT_BE_FUTURE

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_put_music_wrong_release_date_format(self):

        self.minimal_attributes_music['release_date'] = self.minimal_attributes_music.get(
            'release_date').replace('-', '/')

        response = client.put(
            reverse(
                'get_update_delete_music',
                kwargs={
                    'id': self.music.id
                }
            ),
            data=json.dumps(self.minimal_attributes_music),
            content_type='application/json',
            **self.header_user1
        )

        expected_message = messages.WRONG_RELEASE_DATE_FORMAT

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_put_music_wrong_duration_format(self):

        self.minimal_attributes_music['duration'] = self.minimal_attributes_music.get(
            'duration').replace(':', '/')

        response = client.put(
            reverse(
                'get_update_delete_music',
                kwargs={
                    'id': self.music.id
                }
            ),
            data=json.dumps(self.minimal_attributes_music),
            content_type='application/json',
            **self.header_user1
        )

        expected_message = messages.WRONG_DURATION_FORMAT

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_put_music_with_invalid_release_date(self):

        self.minimal_attributes_music['release_date'] = '2021-01-32'

        response = client.put(
            reverse(
                'get_update_delete_music',
                kwargs={
                    'id': self.music.id
                }
            ),
            data=json.dumps(self.minimal_attributes_music),
            content_type='application/json',
            **self.header_user1
        )

        expected_message = messages.get_invalid_date(
            self.minimal_attributes_music['release_date'])

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_put_music_with_invalid_duration(self):

        self.minimal_attributes_music['duration'] = '23:60:59'

        response = client.put(
            reverse(
                'get_update_delete_music',
                kwargs={
                    'id': self.music.id
                }
            ),
            data=json.dumps(self.minimal_attributes_music),
            content_type='application/json',
            **self.header_user1
        )

        expected_message = messages.get_invalid_time(
            self.minimal_attributes_music['duration'])

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    @parameterized.expand([
        (base_tdd.INVALID_TOKEN_HEADER, messages.INVALID_TOKEN),
        (base_tdd.EMPTY_AUTHORIZATION_HEADER,
         messages.HEADER_AUTHORIZATION_NOT_PRESENT),
        (base_tdd.NO_TOKEN_HEADER, messages.NO_TOKEN_PROVIDED),
    ])
    def test_put_music_with_inappropriate_tokens(self, header, expected_message):

        response = client.put(
            reverse(
                'get_update_delete_music',
                kwargs={
                    'id': self.music.id
                }
            ),
            data=json.dumps(self.minimal_attributes_music),
            content_type='application/json',
            **header
        )

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_put_music_without_authorization_header(self):

        response = client.put(
            reverse(
                'get_update_delete_music',
                kwargs={
                    'id': self.music.id
                }
            ),
            data=json.dumps(self.minimal_attributes_music),
            content_type='application/json'
        )

        expected_message = messages.HEADER_AUTHORIZATION_NOT_PRESENT

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_music_without_bearer_authentication_scheme(self):

        response = client.put(
            reverse(
                'get_update_delete_music',
                kwargs={
                    'id': self.music.id
                }
            ),
            data=json.dumps(self.minimal_attributes_music),
            content_type='application/json',
            **base_tdd.get_no_bearer_header(self.header_user1)
        )

        expected_message = messages.NO_BEARER_AUTHENTICATION_SCHEME

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_put_music_with_expired_token(self):

        response = client.put(
            reverse(
                'get_update_delete_music',
                kwargs={
                    'id': self.music.id
                }
            ),
            data=json.dumps(self.minimal_attributes_music),
            content_type='application/json',
            **base_tdd.get_expired_token_header(self.db_user1.id)
        )

        expected_message = messages.TOKEN_EXPIRED

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
