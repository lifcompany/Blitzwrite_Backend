# urls.py

from django.urls import path
from .views import set_keyword, suggest_keywords, add_new_version, get_edit_version, delete_model, delete_files, get_file_content, post_article, run_script, stop_script, set_site, update_model, create_payment_intent, stripe_webhook


urlpatterns = [
    path('set_keyword/', set_keyword, name='set_keyword'),
    path('suggest_keywords/', suggest_keywords, name='suggest_keywords'),
    path('add_new_version/', add_new_version, name='add_new_version'),

]