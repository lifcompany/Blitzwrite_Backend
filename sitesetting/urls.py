# urls.py

from django.urls import path
from .views import get_file_list, GetModel, add_new_version, get_edit_version, delete_model, delete_files, get_file_content, post_article, run_script, stop_script, SetSite, GetSite, get_site_title, update_model, create_payment_intent, stripe_webhook


urlpatterns = [
    path('get_file_list/', get_file_list, name='get_file_list'),
    path('get_model_list/', GetModel.as_view(), name='get_model_list'),
    path('add_new_version/', add_new_version, name='add_new_version'),
    path('update_model/', update_model, name='update_model'),
    path('get_edit_version/', get_edit_version, name='get_edit_version'),
    path('delete_model/', delete_model, name='delete_model'),
    path('delete_files/', delete_files, name='delete_files'),
    path('get_file_content/', get_file_content, name='get_file_content'),
    path('post_article/', post_article, name='post_article'),
    path('run_script/', run_script, name='run_script'),
    path('stop_script/', stop_script, name='stop_script'),
    path('set_site/', SetSite.as_view(), name='set_site'),
    path('get_site/', GetSite.as_view(), name='get_site'),
    path('get-title/', get_site_title, name='get-title'),
    # path('create-payment-intent/', create_payment_intent, name='create-payment-intent'),
    path('create-payment-intent/', create_payment_intent, name='create-payment-intent'),
    path('webhook/', stripe_webhook, name='stripe-webhook'),

]