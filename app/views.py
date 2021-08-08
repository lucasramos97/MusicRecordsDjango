from django.core.paginator import Paginator
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Music
from .serializers import MusicSerializer

@api_view(['GET', 'DELETE', 'PUT'])
def get_delete_update_music(request, pk):
    try:
        music = Music.objects.get(pk=pk)
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

        page = request.GET.get('page') or 1
        size = request.GET.get('size') or 5

        musics = Music.objects.all()
        paginator = Paginator(musics, size)
        serializer = MusicSerializer(paginator.get_page(page), many=True)

        return Response({'content': serializer.data, 'total': paginator.count})
    elif request.method == 'POST':
        return Response({})
