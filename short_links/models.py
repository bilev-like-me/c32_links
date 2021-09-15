from django.db import models
from hashid_field import HashidAutoField, HashidField

class ShortLinks(models.Model):
    id = HashidAutoField(primary_key=True)
    user_subpart = models.CharField(max_length=100)
    date_time = models.DateTimeField('Время создания ссылки', auto_now=True)
    long_link = models.CharField(max_length=2048)
    session_id = models.CharField(max_length=32)
