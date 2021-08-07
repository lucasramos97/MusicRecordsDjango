from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Music
from .serializers import MusicSerializer

@api_view(['GET', 'DELETE', 'PUT'])
def get_delete_update_music(request, pk):
    try:
        Music = Music.objects.get(pk=pk)
    except Music.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response({})
    elif request.method == 'DELETE':
        return Response({})
    elif request.method == 'PUT':
        return Response({})


@api_view(['GET', 'POST'])
def get_post_musics(request):
    if request.method == 'GET':
        musics = Music.objects.all()
        serializer = MusicSerializer(musics, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        return Response({})