from rest_framework import status
from django.test import TestCase
from django.urls import reverse
from parameterized import parameterized
from app import messages
from app.models import Music
from app.tests.factories import MusicFactory, create_user
from . import base_tdd

client = base_tdd.get_client()


class EmptyListTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.db_user1 = create_user()
        cls.header_user1 = base_tdd.generate_header(cls.db_user1)

        cls.db_user2 = create_user('2')

        MusicFactory.create_batch(10, deleted=True, user=cls.db_user1)
        MusicFactory.create_batch(10, deleted=True, user=cls.db_user2)
        MusicFactory.create(user=cls.db_user1)

    def test_empty_list(self):

        response = client.delete(
            reverse('empty_list'),
            **self.header_user1
        )

        db_musics_user1 = Music.objects.filter(user=self.db_user1)
        db_music_user1 = db_musics_user1[0]

        count_musics_user2 = Music.objects.filter(user=self.db_user2).count()

        self.assertEqual(10, response.data)
        self.assertEqual(1, len(db_musics_user1))
        self.assertFalse(db_music_user1.deleted)
        self.assertEqual(10, count_musics_user2)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    @parameterized.expand([
        (base_tdd.INVALID_TOKEN_HEADER, messages.INVALID_TOKEN),
        (base_tdd.EMPTY_AUTHORIZATION_HEADER,
         messages.HEADER_AUTHORIZATION_NOT_PRESENT),
        (base_tdd.NO_TOKEN_HEADER, messages.NO_TOKEN_PROVIDED),
    ])
    def test_empty_list_with_inappropriate_tokens(self, header, expected_message):

        response = client.delete(
            reverse('empty_list'),
            **header
        )

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_empty_list_without_authorization_header(self):

        response = client.delete(
            reverse('empty_list')
        )

        expected_message = messages.HEADER_AUTHORIZATION_NOT_PRESENT

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_empty_list_without_bearer_authentication_scheme(self):

        response = client.delete(
            reverse('empty_list'),
            **base_tdd.get_no_bearer_header(self.header_user1)
        )

        expected_message = messages.NO_BEARER_AUTHENTICATION_SCHEME

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_empty_list_with_expired_token(self):

        response = client.delete(
            reverse('empty_list'),
            **base_tdd.get_expired_token_header(self.db_user1.id)
        )

        expected_message = messages.TOKEN_EXPIRED

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
