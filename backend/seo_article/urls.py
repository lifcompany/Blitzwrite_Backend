# urls.py

from django.urls import path
from .views import set_keyword


urlpatterns = [
    path('set_keyword/', set_keyword, name='set_keyword'),
]