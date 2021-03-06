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


class RestoreDeletedMusicsTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.db_user1 = create_user()
        cls.header_user1 = base_tdd.generate_header(cls.db_user1)

        cls.db_user2 = create_user('2')
        cls.header_user2 = base_tdd.generate_header(cls.db_user2)

    def setUp(self):

        self.deleted_musics = MusicFactory.create_batch(10, deleted=True,
                                                        user=self.db_user1)
        self.musics = MusicFactory.create_batch(1, user=self.db_user1)
        MusicFactory.create_batch(10, deleted=True, user=self.db_user2)

    def test_restore_deleted_musics(self):

        deleted_musics_serializer = MusicSerializer(self.deleted_musics,
                                                    many=True)

        response = client.post(
            reverse('restore_deleted_musics'),
            data=json.dumps(deleted_musics_serializer.data),
            content_type='application/json',
            **self.header_user1
        )

        count_musics_user1 = Music.objects.filter(deleted=False,
                                                  user=self.db_user1).count()
        count_deleted_musics_user2 = Music.objects.filter(deleted=True,
                                                          user=self.db_user2).count()

        self.assertEqual(10, response.data)
        self.assertEqual(11, count_musics_user1)
        self.assertEqual(10, count_deleted_musics_user2)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_restore_deleted_nonexistent_musics_by_id(self):

        changed_music = self.deleted_musics.pop(0)
        changed_music.id = 1000
        self.deleted_musics.append(changed_music)

        deleted_musics_serializer = MusicSerializer(self.deleted_musics,
                                                    many=True)

        response = client.post(
            reverse('restore_deleted_musics'),
            data=json.dumps(deleted_musics_serializer.data),
            content_type='application/json',
            **self.header_user1
        )

        count_musics_user1 = Music.objects.filter(deleted=False,
                                                  user=self.db_user1).count()
        count_deleted_musics_user2 = Music.objects.filter(deleted=True,
                                                          user=self.db_user2).count()

        self.assertEqual(9, response.data)
        self.assertEqual(10, count_musics_user1)
        self.assertEqual(10, count_deleted_musics_user2)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_restore_deleted_non_deleted_musics(self):

        musics_serializer = MusicSerializer(self.musics, many=True)

        response = client.post(
            reverse('restore_deleted_musics'),
            data=json.dumps(musics_serializer.data),
            content_type='application/json',
            **self.header_user1
        )

        db_musics_user1 = Music.objects.filter(user=self.db_user1)
        count_deleted_musics_user2 = Music.objects.filter(deleted=True,
                                                          user=self.db_user2).count()

        self.assertEqual(0, response.data)
        self.assertEqual(11, len(db_musics_user1))
        self.assertTrue(any(not music.deleted for music in db_musics_user1))
        self.assertEqual(10, count_deleted_musics_user2)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_restore_deleted_nonexistent_musics_by_user(self):

        deleted_musics_serializer = MusicSerializer(self.deleted_musics,
                                                    many=True)

        response = client.post(
            reverse('restore_deleted_musics'),
            data=json.dumps(deleted_musics_serializer.data),
            content_type='application/json',
            **self.header_user2
        )

        count_musics_user1 = Music.objects.filter(deleted=False,
                                                  user=self.db_user1).count()
        count_deleted_musics_user2 = Music.objects.filter(deleted=True,
                                                          user=self.db_user2).count()

        self.assertEqual(0, response.data)
        self.assertEqual(1, count_musics_user1)
        self.assertEqual(10, count_deleted_musics_user2)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_restore_deleted_musics_without_id_field(self):

        deleted_musics_serializer = MusicSerializer(self.deleted_musics,
                                                    many=True)

        response = client.post(
            reverse('restore_deleted_musics'),
            data=json.dumps(deleted_musics_serializer.data).replace(
                'id', 'none', 1),
            content_type='application/json',
            **self.header_user1
        )

        self.assertEqual(messages.ID_IS_REQUIRED, response.data.get('message'))
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    @parameterized.expand([
        (base_tdd.INVALID_TOKEN_HEADER, messages.INVALID_TOKEN),
        (base_tdd.EMPTY_AUTHORIZATION_HEADER,
         messages.HEADER_AUTHORIZATION_NOT_PRESENT),
        (base_tdd.NO_TOKEN_HEADER, messages.NO_TOKEN_PROVIDED),
    ])
    def test_restore_deleted_musics_with_inappropriate_tokens(self, header, expected_message):

        deleted_musics_serializer = MusicSerializer(self.deleted_musics,
                                                    many=True)

        response = client.post(
            reverse('restore_deleted_musics'),
            data=json.dumps(deleted_musics_serializer.data),
            content_type='application/json',
            **header
        )

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_restore_deleted_musics_without_authorization_header(self):

        deleted_musics_serializer = MusicSerializer(self.deleted_musics,
                                                    many=True)

        response = client.post(
            reverse('restore_deleted_musics'),
            data=json.dumps(deleted_musics_serializer.data),
            content_type='application/json'
        )

        expected_message = messages.HEADER_AUTHORIZATION_NOT_PRESENT

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_restore_deleted_musics_without_bearer_authentication_scheme(self):

        deleted_musics_serializer = MusicSerializer(self.deleted_musics,
                                                    many=True)

        response = client.post(
            reverse('restore_deleted_musics'),
            data=json.dumps(deleted_musics_serializer.data),
            content_type='application/json',
            **base_tdd.get_no_bearer_header(self.header_user1)
        )

        expected_message = messages.NO_BEARER_AUTHENTICATION_SCHEME

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_restore_deleted_musics_with_expired_token(self):

        deleted_musics_serializer = MusicSerializer(self.deleted_musics,
                                                    many=True)

        response = client.post(
            reverse('restore_deleted_musics'),
            data=json.dumps(deleted_musics_serializer.data),
            content_type='application/json',
            **base_tdd.get_expired_token_header(self.db_user1.id)
        )

        expected_message = messages.TOKEN_EXPIRED

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
