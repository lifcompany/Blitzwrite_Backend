from django.db import models

class LifVersion(models.Model):
    display_name = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    endpoint = models.URLField()
    params = models.TextField()

    def __str__(self):
        return self.display_name

class SiteData(models.Model):
    site_name = models.CharField(max_length=255)
    site_url = models.URLField(max_length=200)
    admin_name = models.CharField(max_length=255)
    admin_pass = models.CharField(max_length=255)

    def __str__(self):
        return self.site_name