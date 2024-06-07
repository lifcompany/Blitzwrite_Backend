# urls.py

from django.urls import path
from .views import set_keyword, get_model_list, add_new_version, get_edit_version, delete_model, delete_files, get_file_content, post_article, run_script, stop_script, set_site, update_model, create_payment_intent, stripe_webhook


urlpatterns = [
    path('set_keyword/', set_keyword, name='set_keyword'),
    path('get_model_list/', get_model_list, name='get_model_list'),
    path('add_new_version/', add_new_version, name='add_new_version'),

]