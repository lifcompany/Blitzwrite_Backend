from django.db import models

class LifVersion(models.Model):
    display_name = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    endpoint = models.URLField()
    params = models.TextField()

    def __str__(self):
        return self.display_name