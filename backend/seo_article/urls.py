from django.urls import path
from .views import autosuggest

urlpatterns = [
    path('auto-suggest/', autosuggest, name='autosuggest'),
]
