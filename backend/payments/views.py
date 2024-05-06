from django.shortcuts import render

# Create your views here.
# views.py

from django.shortcuts import render
from django.conf import settings
from .forms import PaymentForm
import stripe

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

def payment_view(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            token = stripe.Token.create(
                card={
                    'number': form.cleaned_data['card_number'],
                    'exp_month': form.cleaned_data['exp_month'],
                    'exp_year': form.cleaned_data['exp_year'],
                    'cvc': form.cleaned_data['cvc'],
                },
            )
            stripe.Charge.create(
                amount=int(amount * 100),  # amount in cents
                currency='usd',
                source=token.id,
            )
            # Payment successful
            return render(request, 'success.html')
    else:
        form = PaymentForm()
    return render(request, 'payment.html', {'form': form})
