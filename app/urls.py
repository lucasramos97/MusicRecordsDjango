from django.conf.urls import url
from app.views import music_views, user_views

urlpatterns = [

    # User URL's
    url(
        r'^login/?$',
        user_views.login,
        name='login'
    ),
    url(
        r'^users/?$',
        user_views.create_user,
        name='create_user'
    ),

    # Music URL's
    url(
        r'^musics/(?P<id>[0-9]+)$',
        music_views.get_update_delete_music,
        name='get_update_delete_music'
    ),
    url(
        r'^musics/?$',
        music_views.get_post_musics,
        name='get_post_musics'
    ),
    url(
        r'^musics/deleted/count/?$',
        music_views.count_deleted_musics,
        name='count_deleted_musics'
    ),
    url(
        r'^musics/deleted/?$',
        music_views.get_deleted_musics,
        name='get_deleted_musics'
    ),
    url(
        r'^musics/deleted/restore/?$',
        music_views.restore_deleted_musics,
        name='restore_deleted_musics'
    ),
    url(
        r'^musics/definitive/(?P<id>[0-9]+)$',
        music_views.definitive_delete_music,
        name='definitive_delete_music'
    ),
    url(
        r'^musics/empty-list/?$',
        music_views.empty_list,
        name='empty_list'
    ),
]
