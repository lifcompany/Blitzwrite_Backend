# urls.py

from django.urls import path
from .views import set_keyword, suggest_keywords


urlpatterns = [
    path('set_keyword/', set_keyword, name='set_keyword'),
    path('suggest_keywords/', suggest_keywords, name='suggest_keywords'),

]