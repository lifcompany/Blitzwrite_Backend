# urls.py

from django.urls import path
from .views import get_file_list, get_model_list, add_new_version, get_edit_version, delete_model, delete_files


urlpatterns = [
    path('get_file_list/', get_file_list, name='get_file_list'),
    path('get_model_list/', get_model_list, name='get_model_list'),
    path('add_new_version/', add_new_version, name='add_new_version'),
    path('get_edit_version/', get_edit_version, name='get_edit_version'),
    path('delete_model/', delete_model, name='delete_model'),
    path('delete_files/', delete_files, name='delete_files'),
]