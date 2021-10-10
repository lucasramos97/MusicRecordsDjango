import datetime
import jwt
from django.core.validators import validate_email
from django.db import IntegrityError
from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import FieldError, ValidationError
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from app import messages
from app.models import User
from app.serializers import UserSerializer


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
            message = messages.get_email_already_registered(
                request.data.get('email'))

        return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)
    except ValidationError:
        return Response({'message': messages.EMAIL_INVALID}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):

    try:

        (email, password) = __valid_login(request)
        validate_email(email)
        user = User.objects.get(email=email)
        if not user.check_password(password):
            message = messages.get_password_does_not_match_with_email(email)
            return Response({'message': message}, status=status.HTTP_401_UNAUTHORIZED)

        token = jwt.encode({'user_id': user.id, 'exp': __token_expiration_time()},
                           settings.SECRET_KEY, algorithm='HS256')

        return Response({
            'token': token,
            'username': user.username,
            'email': user.email,
        }, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'message': messages.get_user_not_found_by_email(email)}, status=status.HTTP_401_UNAUTHORIZED)
    except FieldError as e:
        return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except ValidationError:
        return Response({'message': messages.EMAIL_INVALID}, status=status.HTTP_400_BAD_REQUEST)


def __valid_login(request):

    email = request.data.get('email')
    if not email:
        raise FieldError(messages.EMAIL_IS_REQUIRED)

    validate_email(email)

    password = request.data.get('password')
    if not password:
        raise FieldError(messages.PASSWORD_IS_REQUIRED)

    return (email, password)


def __valid_user(request):

    username = request.data.get('username')
    if not username:
        raise FieldError(messages.USERNAME_IS_REQUIRED)

    (email, password) = __valid_login(request)
    return (username, email, password)


def __token_expiration_time():
    return datetime.datetime.today() + datetime.timedelta(days=1)
