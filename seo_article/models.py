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
    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.content}"
    
class Article(models.Model):
    STATUS_CHOICES = [
        ('public', 'Public'),
        ('draft', 'Draft'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    site_url = models.CharField(max_length=255, default='')
    keywords = models.TextField(max_length=255)  # Store keywords as a comma-separated string
    amount = models.IntegerField(default=0)  # Store keywords as a comma-separated string
    wp_status = models.CharField(max_length=10)
    category = models.CharField(max_length=255, blank=True, null=True)  # New field for category
    current_clicks = models.IntegerField(default=0)  # New field for current clicks, initialized to 0
    last_month_clicks = models.IntegerField(default=0)  # New field for last month's clicks, initialized to 0
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title