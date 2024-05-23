from django.shortcuts import render
import os
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import LifVersion
import json

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


@method_decorator(csrf_exempt, name='dispatch')
@require_POST
def add_new_version(request):
    try:
        data = json.loads(request.body)

        editversionID = data.get('editversionID')
        display_name = data['display_name']
        model_name = data['model_name']
        endpoint = data['endpoint']
        params = data['params']

        if editversionID:
            try:
                model_version = LifVersion.objects.get(id=editversionID)
            except LifVersion.DoesNotExist:
                return JsonResponse({'error': 'Model version not found'}, status=404)

            # Check for uniqueness constraints
            if LifVersion.objects.exclude(id=editversionID).filter(display_name=display_name).exists():
                return JsonResponse({'error': 'A model with the same display name already exists.'}, status=409)
            if LifVersion.objects.exclude(id=editversionID).filter(model_name=model_name).exists():
                return JsonResponse({'error': 'A model with the same model name already exists.'}, status=409)

            # Update existing model version
            model_version.display_name = display_name
            model_version.model_name = model_name
            model_version.endpoint = endpoint
            model_version.params = params
            model_version.save()
            message = "Model updated successfully"
        else:
            # Check for uniqueness constraints
            if LifVersion.objects.filter(display_name=display_name).exists():
                return JsonResponse({'error': 'A model with the same display name already exists.'}, status=409)
            if LifVersion.objects.filter(model_name=model_name).exists():
                return JsonResponse({'error': 'A model with the same model name already exists.'}, status=409)

            # Create new model version
            LifVersion.objects.create(
                display_name=display_name,
                model_name=model_name,
                endpoint=endpoint,
                params=params
            )
            message = "Model added successfully"

        return JsonResponse({'message': message}, status=201)

    except KeyError as e:
        return JsonResponse({'error': f"Missing data: {str(e)}"}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_edit_version(request):
    try:
        data = json.loads(request.body)
        model_id = data.get('editversionID')

        if model_id:
            try:
                model_version = LifVersion.objects.get(id=model_id)
                model_data = {
                    "display_name": model_version.display_name,
                    "model_name": model_version.model_name,
                    "endpoint": model_version.endpoint,
                    "params": model_version.params,
                }
                return JsonResponse(model_data, status=200)
            except LifVersion.DoesNotExist:
                return JsonResponse({'error': 'Model version not found'}, status=404)
        else:
            return JsonResponse({'error': 'Invalid editversionID format'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def delete_model(request):
    try:
        data = json.loads(request.body)
        delete_model_id = data.get('id')

        if delete_model_id:
            try:
                model_version = LifVersion.objects.get(id=delete_model_id)
                model_version.delete()
                return JsonResponse({"success": "Document deleted"}, status=200)
            except LifVersion.DoesNotExist:
                return JsonResponse({"error": "Document not found or already deleted"}, status=404)
        else:
            return JsonResponse({"error": "Invalid model ID format"}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def delete_files(request):
    try:
        data = json.loads(request.body)
        filename = data.get('filename')

        if not filename:
            return JsonResponse({'success': False, 'message': 'Filename not provided'}, status=400)

        # Ensure the files directory is configured in settings
        files_directory = settings.FILES_DIRECTORY
        file_path = os.path.join(files_directory, filename)

        if os.path.exists(file_path):
            os.remove(file_path)
            return JsonResponse({'success': True, 'message': 'File deleted successfully.'})
        else:
            return JsonResponse({'success': False, 'message': 'File not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON format'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)