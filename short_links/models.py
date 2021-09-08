from django.db import models
from hashid_field import HashidAutoField

class ShortLinks(models.Model):
    id = HashidAutoField(primary_key=True)
    long_link = models.CharField(max_length=2048)
