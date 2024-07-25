from django.db import models
from users.models import User


class Keyword(models.Model):
    name = models.CharField(max_length=255)
    volume = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class MainKeyword(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='main_keywords')
    keyword = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.keyword

class SuggestedKeyword(models.Model):
    main_keyword = models.ForeignKey(MainKeyword, on_delete=models.CASCADE, related_name='suggested_keywords')
    keyword = models.CharField(max_length=255)
    volume = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.keyword

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    credits = models.IntegerField(default=5)

    def __str__(self):
        return self.user.username