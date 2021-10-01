import factory
from faker import Factory
from app.models import Music, User

fake = Factory.create()


class MusicFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Music

    title = ' '.join(fake.words())
    artist = fake.name()
    release_date = fake.date()
    duration = fake.time()
    number_views = fake.random_int()
    feat = fake.pybool()


def create_user(complement='1'):
    return User.objects.create_user(
        username='user{}'.format(complement),
        email='user{}@email.com'.format(complement),
        password='123'
    )
