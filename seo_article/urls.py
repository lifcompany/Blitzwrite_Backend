from django.urls import path
from .views import autosuggest, KeywordSuggest, SendNotificationEmail, SaveKeywords, CreateHeading, CreateConfig, GetUserCredit, CreateArticle,GetKeywordData

urlpatterns = [
    path('auto-suggest/', autosuggest, name='autosuggest'),
    path('keyword-suggest/', KeywordSuggest.as_view(), name='keywordsuggest'),
    path('send-notification/', SendNotificationEmail.as_view(), name='sendnotification'),
    path('save_keywords/', SaveKeywords.as_view(), name='save_keywords'),

    path('get-user-credit/', GetUserCredit.as_view(), name='get_user_profile'),
    path('get-keyword-data/', GetKeywordData.as_view(), name='get_keyword_data'),
    
    path('create-heading/', CreateHeading.as_view(), name='create_heading'),
    path('create-config/', CreateConfig.as_view(), name='create_config'),
    path('create-article/', CreateArticle.as_view(), name='create_article'),
]
