from django.urls import path
from .views import autosuggest, KeywordSuggest, SendNotificationEmail, SaveKeywords, CreateHeading

urlpatterns = [
    path('auto-suggest/', autosuggest, name='autosuggest'),
    path('keyword-suggest/', KeywordSuggest.as_view(), name='keywordsuggest'),
    path('send-notification/', SendNotificationEmail.as_view(), name='sendnotification'),
    path('save_keywords/', SaveKeywords.as_view(), name='save_keywords'),
    path('create-heading/', CreateHeading.as_view(), name='create_heading'),
]
