from rest_framework import status
from django.test import TestCase
from django.urls import reverse
from parameterized import parameterized
from app.serializers import MusicSerializer
from app.tests.factories import MusicFactory, create_user
from .base_tdd import (EMPTY_AUTHORIZATION_HEADER, INVALID_TOKEN_HEADER,
                       NO_TOKEN_HEADER, generate_header, get_no_bearer_header,
                       get_client)
from app.messages import (HEADER_AUTHORIZATION_NOT_PRESENT, INVALID_TOKEN,
                          MUSIC_NOT_FOUND, NO_BEARER_AUTHENTICATION_SCHEME,
                          NO_TOKEN_PROVIDED)

client = get_client()


class GetMusicByIdTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.db_user1 = create_user()
        cls.header_user1 = generate_header(cls.db_user1)
        cls.header_user2 = generate_header(create_user('2'))

        cls.music = MusicFactory.create(user=cls.db_user1)
        cls.deleted_music = MusicFactory.create(deleted=True,
                                                user=cls.db_user1)

    def test_get_music_by_id(self):

        response = client.get(
            reverse(
                'get_update_delete_music',
                kwargs={
                    'id': self.music.id
                }
            ),
            **self.header_user1
        )

        serializer = MusicSerializer(self.music)

        self.assertEqual(serializer.data, response.data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_get_nonexistent_music_by_id(self):

        response = client.get(
            reverse(
                'get_update_delete_music',
                kwargs={
                    'id': 100
                }
            ),
            **self.header_user1
        )

        self.assertEqual(MUSIC_NOT_FOUND, response.data.get('message'))
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_get_deleted_music_by_id(self):

        response = client.get(
            reverse(
                'get_update_delete_music',
                kwargs={
                    'id': self.deleted_music.id
                }
            ),
            **self.header_user1
        )

        self.assertEqual(MUSIC_NOT_FOUND, response.data.get('message'))
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_get_nonexistent_music_by_user(self):

        response = client.get(
            reverse(
                'get_update_delete_music',
                kwargs={
                    'id': self.music.id
                }
            ),
            **self.header_user2
        )

        self.assertEqual(MUSIC_NOT_FOUND, response.data.get('message'))
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    @parameterized.expand([
        (INVALID_TOKEN_HEADER, INVALID_TOKEN),
        (EMPTY_AUTHORIZATION_HEADER, HEADER_AUTHORIZATION_NOT_PRESENT),
        (NO_TOKEN_HEADER, NO_TOKEN_PROVIDED),
    ])
    def test_get_music_by_id_with_inappropriate_tokens(self, header, expected_message):

        response = client.get(
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

    def test_get_music_by_id_without_authorization_header(self):

        response = client.get(
            reverse(
                'get_update_delete_music',
                kwargs={
                    'id': self.music.id
                }
            )
        )

        expected_message = HEADER_AUTHORIZATION_NOT_PRESENT

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_get_music_by_id_without_bearer_authentication_scheme(self):

        response = client.get(
            reverse(
                'get_update_delete_music',
                kwargs={
                    'id': self.music.id
                }
            ),
            **get_no_bearer_header(self.header_user1)
        )

        expected_message = NO_BEARER_AUTHENTICATION_SCHEME

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
