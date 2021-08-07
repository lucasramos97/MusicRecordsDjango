from django.conf.urls import url
from . import views

urlpatterns = [
    url(
        r'^musics/(?P<pk>[0-9]+)$',
        views.get_delete_update_music,
        name='get_delete_update_music'
    ),
    url(
        r'^musics/$',
        views.get_post_musics,
        name='get_post_musics'
    )
]