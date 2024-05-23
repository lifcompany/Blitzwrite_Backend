from django.shortcuts import render
import os
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import LifVersion

def get_file_list(request):
    directory = './result'
    file_list = os.listdir(directory)
    file_list.sort(key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=False)
    print(file_list)
    return JsonResponse(file_list, safe=False)

def get_model_list(request):
    models = LifVersion.objects.all()
    model_list = []
    for model in models:
        model_dict = {
            'id': model.id,
            'display_name': model.display_name,
            'model_name': model.model_name,
            'endpoint': model.endpoint,
            'params': model.params,
        }
        model_list.append(model_dict)
    
    return JsonResponse(model_list, safe=False)