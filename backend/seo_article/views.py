import requests
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt

@require_GET
@csrf_exempt
def autosuggest(request):
    query = request.GET.get('q', '')
    client = request.GET.get('client', 'chrome')
    
    if len(query) > 2:
        url = 'https://google.de/complete/search'
        params = {
            'q': query,
            'client': client
        }
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            return JsonResponse(response.json(), safe=False)
        else:
            return JsonResponse({'error': 'Failed to fetch suggestions'}, status=response.status_code)
    else:
        return JsonResponse({'error': 'Query too short'}, status=400)
