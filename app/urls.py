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
    ),
    url(
        r'^musics/deleted/count/?$',
        views.count_deleted_musics,
        name='count_deleted_musics'
    ),
    url(
        r'^musics/deleted/?$',
        views.get_deleted_musics,
        name='get_deleted_musics'
    ),
    url(
        r'^musics/deleted/restore/?$',
        views.restore_deleted_musics,
        name='restore_deleted_musics'
    ),
    url(
        r'^musics/empty-list/?$',
        views.empty_list,
        name='empty_list'
    ),
    url(
        r'^musics/definitive/(?P<id>[0-9]+)$',
        views.definitive_delete_music,
        name='definitive_delete_music'
    ),
]
