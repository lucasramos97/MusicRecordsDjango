from django.db import models

# Create your models here.
class Music(models.Model):
    class Meta:
        db_table = 'musics'
    
    title = models.CharField(max_length=100)
    artist = models.CharField(max_length=100)
    release_date = models.DateField()
    duration = models.DurationField()
    number_views = models.IntegerField(default=0)
    feat = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)