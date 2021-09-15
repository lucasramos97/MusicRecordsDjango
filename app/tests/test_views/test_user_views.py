import json
from rest_framework import status
from django.test import TestCase, Client
from django.urls import reverse
from app.models import User

client = Client()


class LoginTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.user = {
            'username': 'test',
            'email': 'test@email.com',
            'password': '123'
        }

        User.objects.create_user(
            username=cls.user['username'],
            email=cls.user['email'],
            password=cls.user['password']
        )

    def test_login(self):

        response = client.post(
            reverse('login'),
            data=json.dumps(self.user),
            content_type='application/json'
        )

        self.assertIsNotNone(response.data['token'])
        self.assertEqual(response.data['username'], self.user['username'])
        self.assertEqual(response.data['email'], self.user['email'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_without_email_field(self):

        self.user['email'] = ''

        response = client.post(
            reverse('login'),
            data=json.dumps(self.user),
            content_type='application/json'
        )

        self.assertEqual(response.data['message'], 'E-mail is required!')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_without_password_field(self):

        self.user['password'] = ''

        response = client.post(
            reverse('login'),
            data=json.dumps(self.user),
            content_type='application/json'
        )

        self.assertEqual(response.data['message'], 'Password is required!')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_invalid_email(self):

        self.user['email'] = 'test'

        response = client.post(
            reverse('login'),
            data=json.dumps(self.user),
            content_type='application/json'
        )

        self.assertEqual(response.data['message'], 'E-mail invalid!')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_invalid_password(self):

        self.user['password'] = '321'

        response = client.post(
            reverse('login'),
            data=json.dumps(self.user),
            content_type='application/json'
        )

        self.assertEqual(response.data['message'], 'Password invalid!')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_with_nonexistent_email(self):

        self.user['email'] = 'test2@email.com'

        response = client.post(
            reverse('login'),
            data=json.dumps(self.user),
            content_type='application/json'
        )

        expected_message = 'User not found by e-mail: {}!'.format(
            self.user['email'])

        self.assertEqual(response.data['message'], expected_message)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CreateUserTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.user = {
            'username': 'test',
            'email': 'test@email.com',
            'password': '123',
        }

    def test_create_user(self):

        response = client.post(
            reverse('create_user'),
            data=json.dumps(self.user),
            content_type='application/json'
        )

        self.assertEqual(response.data['username'], self.user['username'])
        self.assertEqual(response.data['email'], self.user['email'])
        self.assertNotEqual(response.data['password'], self.user['password'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_user_without_username_field(self):

        self.user['username'] = ''
        response = client.post(
            reverse('create_user'),
            data=json.dumps(self.user),
            content_type='application/json'
        )

        self.assertEqual(response.data['message'], 'Username is required!')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_without_email_field(self):

        self.user['email'] = ''

        response = client.post(
            reverse('create_user'),
            data=json.dumps(self.user),
            content_type='application/json'
        )

        self.assertEqual(response.data['message'], 'E-mail is required!')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_without_password_field(self):

        self.user['password'] = ''

        response = client.post(
            reverse('create_user'),
            data=json.dumps(self.user),
            content_type='application/json'
        )

        self.assertEqual(response.data['message'], 'Password is required!')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_with_existent_email(self):

        client.post(
            reverse('create_user'),
            data=json.dumps(self.user),
            content_type='application/json'
        )

        response = client.post(
            reverse('create_user'),
            data=json.dumps(self.user),
            content_type='application/json'
        )

        expected_message = 'The {} e-mail has already been registered!'.format(
            self.user['email'])

        self.assertEqual(response.data['message'], expected_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
