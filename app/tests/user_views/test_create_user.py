import json
from parameterized import parameterized
from rest_framework import status
from django.test import TestCase, Client
from django.urls import reverse
from app.models import User
from app.serializers import UserSerializer
from app.tests.factories import create_user
from app.messages import (EMAIL_IS_REQUIRED, PASSWORD_IS_REQUIRED,
                          USERNAME_IS_REQUIRED, get_email_already_registered)

client = Client()


class CreateUserTest(TestCase):

    def setUp(self):

        self.all_atributes_user = {
            'username': 'user1',
            'email': 'user1@email.com',
            'password': '123',
        }

    def test_create_user(self):

        response = client.post(
            reverse('create_user'),
            data=json.dumps(self.all_atributes_user),
            content_type='application/json'
        )

        response_serializer = response.data

        db_user = User.objects.get(id=response_serializer.get('id'))
        db_user_serializer = UserSerializer(db_user).data

        valid_username = self.all_atributes_user.get('username') == db_user_serializer.get(
            'username') == response_serializer.get('username')

        valid_email = self.all_atributes_user.get('email') == db_user_serializer.get(
            'email') == response_serializer.get('email')

        self.assertTrue(valid_username)
        self.assertTrue(valid_email)
        self.assertNotEqual(self.all_atributes_user.get('password'),
                            db_user_serializer.get('password'))

        self.assertEqual(db_user_serializer.get('password'),
                         response_serializer.get('password'))

        self.assertIsNotNone(response_serializer.get('created_at'))
        self.assertIsNotNone(response_serializer.get('updated_at'))
        self.assertEqual(db_user_serializer.get('created_at'),
                         response_serializer.get('created_at'))

        self.assertEqual(db_user_serializer.get('updated_at'),
                         response_serializer.get('updated_at'))

        self.assertEqual(response_serializer.get('created_at'),
                         response_serializer.get('updated_at'))

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    @parameterized.expand([
        ('username', USERNAME_IS_REQUIRED),
        ('email', EMAIL_IS_REQUIRED),
        ('password', PASSWORD_IS_REQUIRED),
    ])
    def test_create_user_without_required_fields(self, field, expected_message):

        self.all_atributes_user[field] = ''

        response = client.post(
            reverse('create_user'),
            data=json.dumps(self.all_atributes_user),
            content_type='application/json'
        )

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_create_user_with_existent_email(self):

        create_user()

        response = client.post(
            reverse('create_user'),
            data=json.dumps(self.all_atributes_user),
            content_type='application/json'
        )

        expected_message = get_email_already_registered(
            self.all_atributes_user.get('email'))

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)