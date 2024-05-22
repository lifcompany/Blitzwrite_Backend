# forms.py

from django import forms

class PaymentForm(forms.Form):
    amount = forms.DecimalField(label='Amount ($)', max_digits=8, decimal_places=2)
    card_number = forms.CharField(label='Card Number', max_length=16)
    exp_month = forms.IntegerField(label='Expiry Month (MM)')
    exp_year = forms.IntegerField(label='Expiry Year (YYYY)')
    cvc = forms.CharField(label='CVC', max_length=4)
