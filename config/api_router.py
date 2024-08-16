from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from users.views import UserViewSet
from django.urls import path, include
from seo_article.views import NotificationViewSet, ArticleViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'articles', ArticleViewSet, basename='articles')

sub_urls = [
    path('authentication/', include('users.urls')),
    path('setting/', include('sitesetting.urls')),
    path('generate/', include('seo_article.urls')),
]

app_name = "api"
urlpatterns = router.urls + sub_urls
