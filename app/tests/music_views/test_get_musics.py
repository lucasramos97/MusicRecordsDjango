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


class GetMusicsTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.db_user1 = create_user()
        cls.header_user1 = base_tdd.generate_header(cls.db_user1)

        MusicFactory.create_batch(10, user=cls.db_user1)
        MusicFactory.create_batch(10, user=create_user('2'))
        MusicFactory.create(deleted=True, user=cls.db_user1)

    def test_get_musics_with_default_query_params(self):

        response = client.get(
            reverse('get_post_musics'),
            **self.header_user1
        )

        db_musics = Music.objects.filter(deleted=False, user=self.db_user1)
        serializer = MusicSerializer(db_musics[:5], many=True)

        self.assertEqual(serializer.data, response.data.get('content'))
        self.assertEqual(5, len(response.data.get('content')))
        self.assertEqual(len(db_musics), response.data.get('total'))
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_get_musics_with_explicit_query_params(self):

        response = client.get(
            reverse('get_post_musics'),
            {'page': 2, 'size': 4},
            **self.header_user1
        )

        db_musics = Music.objects.filter(deleted=False, user=self.db_user1)
        serializer = MusicSerializer(db_musics[4:8], many=True)

        self.assertEqual(serializer.data, response.data.get('content'))
        self.assertEqual(4, len(response.data.get('content')))
        self.assertEqual(len(db_musics), response.data.get('total'))
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    @parameterized.expand([
        (base_tdd.INVALID_TOKEN_HEADER, messages.INVALID_TOKEN),
        (base_tdd.EMPTY_AUTHORIZATION_HEADER,
         messages.HEADER_AUTHORIZATION_NOT_PRESENT),
        (base_tdd.NO_TOKEN_HEADER, messages.NO_TOKEN_PROVIDED),
    ])
    def test_get_musics_with_inappropriate_tokens(self, header, expected_message):

        response = client.get(
            reverse('get_post_musics'),
            **header
        )

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_get_musics_without_authorization_header(self):

        response = client.get(
            reverse('get_post_musics')
        )

        expected_message = messages.HEADER_AUTHORIZATION_NOT_PRESENT

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_get_musics_without_bearer_authentication_scheme(self):

        response = client.get(
            reverse('get_post_musics'),
            **base_tdd.get_no_bearer_header(self.header_user1)
        )

        expected_message = messages.NO_BEARER_AUTHENTICATION_SCHEME

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_get_musics_with_expired_token(self):

        response = client.get(
            reverse('get_post_musics'),
            **base_tdd.get_expired_token_header(self.db_user1.id)
        )

        expected_message = messages.TOKEN_EXPIRED

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
