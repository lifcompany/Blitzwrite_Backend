from django.db import models

# Create your models here.
class LifVersion(models.Model):
    name = models.CharField(max_length=100)