from django.core.paginator import Paginator
from django.core.exceptions import FieldError
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import Music
from ..serializers import MusicSerializer


@api_view(['GET', 'PUT', 'DELETE'])
def get_update_delete_music(request, id):

    try:
        music = __get_music_if_exists(request, id)
    except Music.DoesNotExist:
        return Response({'message': 'Music not found!'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return __get_music_by_id(music)

    if request.method == 'PUT':
        return __put_music(music, request)

    if request.method == 'DELETE':
        return __delete_music(music)


@api_view(['GET', 'POST'])
def get_post_musics(request):

    if request.method == 'GET':
        return __get_musics(request)

    if request.method == 'POST':
        return __post_music(request)


@api_view(['GET'])
def count_deleted_musics(request):

    result = Music.objects.filter(deleted=True, user=request.user).count()

    return Response(result)


@api_view(['GET'])
def get_deleted_musics(request):

    return __get_musics(request, deleted=True)


@api_view(['POST'])
def restore_deleted_musics(request):

    music_ids = [music['id'] for music in request.data]
    result = Music.objects.filter(
        id__in=music_ids, user=request.user).update(deleted=False)

    return Response(result)


@api_view(['DELETE'])
def empty_list(request):

    Music.objects.filter(deleted=True, user=request.user).delete()

    return Response()


@api_view(['DELETE'])
def definitive_delete_music(request, id):

    try:

        music = __get_music_if_not_exists(request, id)
        music.delete()

        return Response()
    except Music.DoesNotExist:
        return Response({'message': 'Music not found!'}, status=status.HTTP_404_NOT_FOUND)


def __get_music_if_exists(request, id):

    music = Music.objects.get(id=id, user=request.user)
    if music.deleted:
        raise Music.DoesNotExist

    return music


def __get_music_by_id(music):

    serializer = MusicSerializer(music)

    return Response(serializer.data)


def __get_musics(request, deleted=False):

    page = request.GET.get('page') or 1
    size = request.GET.get('size') or 5

    musics = Music.objects.filter(deleted=deleted, user=request.user)
    paginator = Paginator(musics, size)
    serializer = MusicSerializer(paginator.get_page(page), many=True)

    return Response({'content': serializer.data, 'total': paginator.count})


def __valid_music(request):

    title = request.data.get('title')
    if not title:
        raise FieldError('Title is required!')

    artist = request.data.get('artist')
    if not artist:
        raise FieldError('Artist is required!')

    release_date = request.data.get('release_date')
    if not release_date:
        raise FieldError('Release Date is required!')

    duration = request.data.get('duration')
    if not duration:
        raise FieldError('Duration is required!')

    return (title, artist, release_date, duration)


def __post_music(request):

    try:

        (title, artist, release_date, duration) = __valid_music(request)
        (music, _) = Music.objects.get_or_create(
            title=title,
            artist=artist,
            release_date=release_date,
            duration=duration,
            number_views=request.data.get('number_views') or 0,
            feat=request.data.get('feat') or False,
            user=request.user
        )
        serializer = MusicSerializer(music)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except FieldError as e:
        return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


def __put_music(music, request):

    try:

        __valid_music(request)
        serializer = MusicSerializer(music, request.data)
        serializer.is_valid()
        serializer.save()
        return Response(serializer.data)
    except FieldError as e:
        return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


def __delete_music(music):

    music.deleted = True
    music.save()
    serializer = MusicSerializer(music)

    return Response(serializer.data)


def __get_music_if_not_exists(request, id):

    music = Music.objects.get(id=id, user=request.user)
    if not music.deleted:
        raise Music.DoesNotExist

    return music
