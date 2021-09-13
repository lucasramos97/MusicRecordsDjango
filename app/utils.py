from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):

    response = exception_handler(exc, context)

    return __response_handler(response.data['detail'])


def __response_handler(detail):

    message = str(detail)
    if message == 'Invalid token.':
        return Response({'message': 'Invalid token!'}, status=status.HTTP_401_UNAUTHORIZED)

    return Response({'message': message}, status=status.HTTP_401_UNAUTHORIZED)
