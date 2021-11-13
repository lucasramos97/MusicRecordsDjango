import jwt
from django.conf import settings
from rest_framework import authentication
from rest_framework import exceptions
from app import messages
from app.models import User


class BearerAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):

        if self._not_authenticate(request):
            return None

        auth = authentication.get_authorization_header(request).split()

        if not auth:
            raise exceptions.AuthenticationFailed(
                messages.HEADER_AUTHORIZATION_NOT_PRESENT)

        scheme = auth[0]

        if scheme != b'Bearer':
            raise exceptions.AuthenticationFailed(
                messages.NO_BEARER_AUTHENTICATION_SCHEME)

        if len(auth) == 1:
            raise exceptions.AuthenticationFailed(messages.NO_TOKEN_PROVIDED)

        token = auth[1]

        try:

            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms='HS256')
        except jwt.exceptions.DecodeError:
            raise exceptions.AuthenticationFailed(messages.INVALID_TOKEN)
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed(messages.TOKEN_EXPIRED)

        return self.authenticate_credentials(payload.get('user_id'))

    def authenticate_credentials(self, user_id):

        try:

            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed(messages.INVALID_TOKEN)

        return (user, None)

    def _not_authenticate(self, request):
        return request.method == 'POST' and (request.path == '/login' or request.path == '/users')
