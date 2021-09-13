import datetime
import jwt
from django.core.validators import validate_email
from django.db import IntegrityError
from django.conf import settings
from django.core.exceptions import FieldError, ValidationError
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from app.models import User
from app.serializers import UserSerializer


@api_view(['POST'])
def login(request):

    try:

        (email, password) = __valid_login(request)
        validate_email(email)
        user = User.objects.get(email=email)
        if not user.check_password(password):
            return Response({'message': 'Password invalid!'}, status=status.HTTP_401_UNAUTHORIZED)

        token = jwt.encode({'user_id': user.id, 'exp': __token_expiration_time()},
                           settings.SECRET_KEY, algorithm='HS256')

        return Response({
            'token': token,
            'username': user.username,
            'email': user.email,
        }, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'message': 'User not found by e-mail: {}!'.format(email)}, status=status.HTTP_401_UNAUTHORIZED)
    except FieldError as e:
        return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except ValidationError:
        return Response({'message': 'E-mail invalid!'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def create_user(request):

    try:

        (username, email, password) = __valid_user(request)
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        serializer = UserSerializer(user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except FieldError as e:
        return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except IntegrityError as e:

        message = str(e)
        if message.split('app_user.')[1] == 'email':
            message = 'The {} e-mail has already been registered!'.format(
                request.data.get('email'))

        return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)


def __valid_login(request):

    email = request.data.get('email')
    if not email:
        raise FieldError('E-mail is required!')

    password = request.data.get('password')
    if not password:
        raise FieldError('Password is required!')

    return (email, password)


def __valid_user(request):

    username = request.data.get('username')
    if not username:
        raise FieldError('Username is required!')

    (email, password) = __valid_login(request)
    return (username, email, password)


def __token_expiration_time():
    return datetime.datetime.utcnow() + datetime.timedelta(days=1)
