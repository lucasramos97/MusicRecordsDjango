import jwt
from django.conf import settings
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed
from jwt.exceptions import DecodeError
from app.models import User


class BearerAuthentication(authentication.TokenAuthentication):

    keyword = 'Bearer'

    def authenticate(self, request):

        if self.__not_authenticate(request):
            return None

        auth = authentication.get_authorization_header(request).split()

        if not auth:
            raise AuthenticationFailed(
                'Header Authorization not present!')

        scheme = auth[0]

        if scheme != self.keyword.encode():
            raise AuthenticationFailed(
                'No Bearer HTTP authentication scheme!')

        if len(auth) == 1:
            raise AuthenticationFailed(
                'No token provided!')

        token = auth[1]

        try:

            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms='HS256')
        except DecodeError:
            raise AuthenticationFailed('Invalid token!')

        return self.authenticate_credentials(payload['user_id'])

    def authenticate_credentials(self, user_id):

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed('Invalid token!')

        if not user.is_active:
            raise AuthenticationFailed('User inactive!')

        return (user, None)

    def __not_authenticate(self, request):
        return request.method == 'POST' and (request.path == '/login' or request.path == '/users')
