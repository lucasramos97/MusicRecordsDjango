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


class DeleteMusicTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.db_user1 = create_user()
        cls.header_user1 = base_tdd.generate_header(cls.db_user1)
        cls.header_user2 = base_tdd.generate_header(create_user('2'))

    def setUp(self):

        self.music = MusicFactory.create(user=self.db_user1)
        self.deleted_music = MusicFactory.create(deleted=True,
                                                 user=self.db_user1)

    def test_delete_music(self):

        response = client.delete(
            reverse(
                'get_update_delete_music',
                kwargs={
                    'id': self.music.id
                }
            ),
            **self.header_user1
        )

        response_serializer = response.data

        music_serializer = MusicSerializer(self.music).data

        db_music = Music.objects.get(id=self.music.id, user=self.db_user1)
        db_music_serializer = MusicSerializer(db_music).data

        valid_created_at = music_serializer.get('created_at') == db_music_serializer.get(
            'created_at') == response_serializer.get('created_at')

        self.assertEqual(db_music_serializer, response_serializer)
        self.assertIsNotNone(base_tdd.match_date(
            response_serializer.get('release_date')))

        self.assertIsNotNone(base_tdd.match_time(
            response_serializer.get('duration')))

        self.assertIsNone(response_serializer.get('deleted'))
        self.assertIsNone(response_serializer.get('user'))
        self.assertTrue(db_music.deleted)
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

    def test_delete_nonexistent_music_by_id(self):

        response = client.delete(
            reverse(
                'get_update_delete_music',
                kwargs={
                    'id': 100
                }
            ),
            **self.header_user1
        )

        expected_message = messages.MUSIC_NOT_FOUND

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_delete_deleted_music(self):

        response = client.delete(
            reverse(
                'get_update_delete_music',
                kwargs={
                    'id': self.deleted_music.id
                }
            ),
            **self.header_user1
        )

        expected_message = messages.MUSIC_NOT_FOUND

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_delete_nonexistent_music_by_user(self):

        response = client.delete(
            reverse(
                'get_update_delete_music',
                kwargs={
                    'id': self.music.id
                }
            ),
            **self.header_user2
        )

        expected_message = messages.MUSIC_NOT_FOUND

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    @parameterized.expand([
        (base_tdd.INVALID_TOKEN_HEADER, messages.INVALID_TOKEN),
        (base_tdd.EMPTY_AUTHORIZATION_HEADER,
         messages.HEADER_AUTHORIZATION_NOT_PRESENT),
        (base_tdd.NO_TOKEN_HEADER, messages.NO_TOKEN_PROVIDED),
    ])
    def test_delete_music_with_inappropriate_tokens(self, header, expected_message):

        response = client.delete(
            reverse(
                'get_update_delete_music',
                kwargs={
                    'id': self.music.id
                }
            ),
            **header
        )

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_delete_music_without_authorization_header(self):

        response = client.delete(
            reverse(
                'get_update_delete_music',
                kwargs={
                    'id': self.music.id
                }
            )
        )

        expected_message = messages.HEADER_AUTHORIZATION_NOT_PRESENT

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_delete_music_without_bearer_authentication_scheme(self):

        response = client.delete(
            reverse(
                'get_update_delete_music',
                kwargs={
                    'id': self.music.id
                }
            ),
            **base_tdd.get_no_bearer_header(self.header_user1)
        )

        expected_message = messages.NO_BEARER_AUTHENTICATION_SCHEME

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_delete_music_with_expired_token(self):

        response = client.delete(
            reverse(
                'get_update_delete_music',
                kwargs={
                    'id': self.music.id
                }
            ),
            **base_tdd.get_expired_token_header(self.db_user1.id)
        )

        expected_message = messages.TOKEN_EXPIRED

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
