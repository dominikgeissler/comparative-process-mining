from django.db import models

# Create your models here.
class Log(models.Model):
    name = models.TextField()
    path = models.TextField()
    content = models.TextField()