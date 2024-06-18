import os
from django.http import FileResponse, Http404, JsonResponse
from openai import OpenAI
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

class Base:
    stop_execution = False

client = OpenAI(api_key=settings.OPENAI_API_KEY)
print(settings.OPENAI_API_KEY)
print(settings.BASE_DIR)

@csrf_exempt 
def set_keyword(request):
    print("111111")
    parameters = {
        "temperature": 0.2,
        "max_tokens": 500,
        "frequency_penalty": 0.0,
        'timeout': 1200
    }
    conversation_history = [{"role": "system", "content": "You are a helpful assistant."},{"role": "user", "content": "Please provide 10 SEO keywords similar to '車買取'"}]
    responses = []
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=conversation_history,
        **parameters
    )
    responses.append(response.choices[0].message.content.strip())
    print(responses)

    return JsonResponse(responses, safe=False)
