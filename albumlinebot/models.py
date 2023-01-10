from django.db import models

# Create your models here.
class Song_list(models.Model):
    check_q = models.CharField(max_length=50, null= False, default='1')
    song_list = models.CharField(max_length=255,null=False)

  