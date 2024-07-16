from backend.users.models import User
from seo_article.models import UserProfile

for user in User.objects.all():
    UserProfile.objects.get_or_create(user=user)