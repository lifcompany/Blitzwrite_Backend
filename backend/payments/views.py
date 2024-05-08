from django.shortcuts import render

# Create your views here.
# views.py

from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import stripe
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



# views.py

from django.conf import settings



stripe.api_key = settings.STRIPE_SECRET_KEY

@csrf_exempt
def create_payment_intent(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        currency = 'usd'  # Set the currency (e.g., USD)
        
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=int(amount),
                currency=currency
            )
            return JsonResponse({
                'clientSecret': payment_intent.client_secret
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def stripe_webhook(request):
    # Handle Stripe webhook events here
    payload = request.body
    sig_header = request.headers.get('Stripe-Signature', None)

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        # Handle the event (e.g., update payment status in database)
        return JsonResponse({'received': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
