from django.conf.urls import url
from . import views

urlpatterns = [
    url(
        r'^musics/(?P<id>[0-9]+)$',
        views.get_update_delete_music,
        name='get_update_delete_music'
    ),
    url(
        r'^musics/?$',
        views.get_post_musics,
        name='get_post_musics'
    )
]