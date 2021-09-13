
from rest_framework import authentication
from rest_framework import exceptions


class BearerAuthentication(authentication.TokenAuthentication):

    keyword = 'Bearer'

    def authenticate(self, request):

        auth = authentication.get_authorization_header(request).split()

        if self.__not_authenticate(request):
            return None

        if not auth:
            raise exceptions.AuthenticationFailed(
                'Header Authorization not present!')

        if auth[0] != self.keyword.encode():
            raise exceptions.AuthenticationFailed(
                'No Bearer HTTP authentication scheme!')

        if len(auth) == 1:
            raise exceptions.AuthenticationFailed(
                'No token provided!')

        token = auth[1].decode()

        return self.authenticate_credentials(token)

    def __not_authenticate(self, request):
        return request.method == 'POST' and (request.path == '/login' or request.path == '/users')
