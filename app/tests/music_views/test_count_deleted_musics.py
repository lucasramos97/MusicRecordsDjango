from rest_framework import status
from django.test import TestCase
from django.urls import reverse
from parameterized import parameterized
from app import messages
from app.tests.factories import MusicFactory, create_user
from . import base_tdd

client = base_tdd.get_client()


class CountDeletedMusicsTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.db_user1 = create_user()
        cls.header_user1 = base_tdd.generate_header(cls.db_user1)

        MusicFactory.create_batch(10, deleted=True, user=cls.db_user1)
        MusicFactory.create(user=cls.db_user1)
        MusicFactory.create(deleted=True, user=create_user('2'))

    def test_count_deleted_music(self):

        response = client.get(
            reverse('count_deleted_musics'),
            **self.header_user1
        )

        self.assertEqual(10, response.data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    @parameterized.expand([
        (base_tdd.INVALID_TOKEN_HEADER, messages.INVALID_TOKEN),
        (base_tdd.EMPTY_AUTHORIZATION_HEADER,
         messages.HEADER_AUTHORIZATION_NOT_PRESENT),
        (base_tdd.NO_TOKEN_HEADER, messages.NO_TOKEN_PROVIDED),
    ])
    def test_count_deleted_music_with_inappropriate_tokens(self, header, expected_message):

        response = client.get(
            reverse('count_deleted_musics'),
            **header
        )

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_count_deleted_music_without_authorization_header(self):

        response = client.get(
            reverse('count_deleted_musics')
        )

        expected_message = messages.HEADER_AUTHORIZATION_NOT_PRESENT

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_count_deleted_music_without_bearer_authentication_scheme(self):

        response = client.get(
            reverse('count_deleted_musics'),
            **base_tdd.get_no_bearer_header(self.header_user1)
        )

        expected_message = messages.NO_BEARER_AUTHENTICATION_SCHEME

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
