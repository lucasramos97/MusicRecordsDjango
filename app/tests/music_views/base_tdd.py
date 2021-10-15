import datetime
import json
import jwt
from django.conf import settings
from django.test import Client
from django.urls import reverse

INVALID_TOKEN_HEADER = {
    'HTTP_AUTHORIZATION': 'Bearer 123'
}

EMPTY_AUTHORIZATION_HEADER = {
    'HTTP_AUTHORIZATION': ''
}

NO_TOKEN_HEADER = {
    'HTTP_AUTHORIZATION': 'Bearer '
}

client = Client()


def get_client():
    return client


def generate_header(user_db):

    user_dict = {
        'email': user_db.email,
        'password': '123'
    }

    user_response = client.post(
        reverse('login'),
        data=json.dumps(user_dict),
        content_type='application/json'
    )

    user_header = {
        'HTTP_AUTHORIZATION': 'Bearer {}'.format(user_response.data.get('token'))
    }

    return user_header


def get_no_bearer_header(header):
    return {
        'HTTP_AUTHORIZATION': header['HTTP_AUTHORIZATION'].replace('Bearer', 'Token')
    }


def get_expired_token_header(user_id):

    _10_seconds_ago = datetime.datetime.today() - datetime.timedelta(seconds=10)

    timestamp = int(_10_seconds_ago.timestamp())

    expired_token = jwt.encode(
        {'user_id': user_id, 'exp': timestamp}, settings.SECRET_KEY, algorithm='HS256')

    return {
        'HTTP_AUTHORIZATION': 'Bearer {}'.format(expired_token)
    }
