# urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('payment/', views.payment_view, name='payment'),
    path('create_payment_intent/', views.create_payment_intent, name='create_payment_intent'),
    path('api/create-payment-intent/', views.create_payment_intent, name='create_payment_intent'),
    path('api/stripe-webhook/', views.stripe_webhook, name='stripe_webhook'),
]
