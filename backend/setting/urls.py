# urls.py

from django.urls import path
from .views import get_file_list, get_model_list


urlpatterns = [
    path('get_file_list/', get_file_list, name='get_file_list'),
    path('get_model_list/', get_model_list, name='get_model_list'),
]