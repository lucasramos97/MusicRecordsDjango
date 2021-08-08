import factory
from faker import Factory
from ..models import Music

fake = Factory.create()

class MusicFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Music

    title = fake.sentence(nb_words=3)
    artist = fake.name()
    release_date = fake.date()
    duration = fake.time_delta()
    number_views = fake.random_int()
    feat = fake.pybool()
