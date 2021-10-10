import json
from rest_framework import status
from django.test import TestCase, Client
from django.urls import reverse
from parameterized import parameterized
from app import messages
from app.tests.factories import create_user

client = Client()


class LoginTest(TestCase):

    def setUp(self):

        self.db_user1 = create_user()

        self.all_attributes_login = {
            'email': self.db_user1.email,
            'password': '123'
        }

    def test_login(self):

        response = client.post(
            reverse('login'),
            data=json.dumps(self.all_attributes_login),
            content_type='application/json'
        )

        response_serializer = response.data

        self.assertIsNotNone(response_serializer.get('token'))
        self.assertNotEqual('', response_serializer.get('token'))
        self.assertEqual(self.db_user1.username,
                         response_serializer.get('username'))

        self.assertEqual(self.all_attributes_login.get('email'),
                         response_serializer.get('email'))

        self.assertIsNone(response.data.get('password'))
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    @parameterized.expand([
        ('email', messages.EMAIL_IS_REQUIRED),
        ('password', messages.PASSWORD_IS_REQUIRED),
    ])
    def test_login_without_required_fields(self, field, expected_message):

        self.all_attributes_login[field] = ''

        response = client.post(
            reverse('login'),
            data=json.dumps(self.all_attributes_login),
            content_type='application/json'
        )

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_login_with_invalid_email(self):

        self.all_attributes_login['email'] = 'test'

        response = client.post(
            reverse('login'),
            data=json.dumps(self.all_attributes_login),
            content_type='application/json'
        )

        self.assertEqual(messages.EMAIL_INVALID, response.data.get('message'))
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_login_with_nonexistent_email(self):

        self.all_attributes_login['email'] = 'user2@email.com'

        response = client.post(
            reverse('login'),
            data=json.dumps(self.all_attributes_login),
            content_type='application/json'
        )

        expected_message = messages.get_user_not_found_by_email(
            self.all_attributes_login.get('email'))

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_login_with_non_matching_password(self):

        self.all_attributes_login['password'] = '321'

        response = client.post(
            reverse('login'),
            data=json.dumps(self.all_attributes_login),
            content_type='application/json'
        )

        expected_message = messages.get_password_does_not_match_with_email(
            self.all_attributes_login.get('email'))

        self.assertEqual(expected_message, response.data.get('message'))
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
