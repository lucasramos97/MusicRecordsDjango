from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):

    response = exception_handler(exc, context)
    message = str(response.data.get('detail'))

    return Response({'message': message}, status=status.HTTP_401_UNAUTHORIZED)
