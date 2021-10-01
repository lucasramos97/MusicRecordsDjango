from rest_framework import serializers
from app.models import Music, User


class BaseSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):

        ret = super().to_representation(instance)
        ret['created_at'] = self.__format_datetime(ret.get('created_at'))
        ret['updated_at'] = self.__format_datetime(ret.get('updated_at'))

        return ret

    def __format_datetime(self, datetime_str):

        if not datetime_str:
            return ''

        datetime_split = datetime_str.split('T')
        date = datetime_split[0]
        time = datetime_split[1].split('-')[0][:-3]

        return '{} {}'.format(date, time)


class UserSerializer(BaseSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email',
                  'password', 'created_at', 'updated_at']


class MusicSerializer(BaseSerializer):
    class Meta:
        model = Music
        exclude = ['deleted', 'user']
