import os
import json
import re
import gspread
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from oauth2client.service_account import ServiceAccountCredentials
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods import posts
from django.views.decorators.http import require_GET
from django.utils.decorators import method_decorator
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
    
def get_file_content(request):
    file_name = request.GET.get('file_name')
    result_folder = './result'  # You might want to set this in your settings file

    if not file_name:
        return JsonResponse({"error": "file_name parameter is required"}, status=400)

    file_path = os.path.join(result_folder, file_name)

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return JsonResponse({"content": content})
    except FileNotFoundError:
        return JsonResponse({"error": "File not found"}, status=404)
    except UnicodeDecodeError:
        return JsonResponse({"error": "Error decoding file. The file may not be in UTF-8 encoding."}, status=500)
    
@method_decorator(csrf_exempt, name='dispatch')
@require_GET
def post_article(request):
    try:
        # Initialize Google Sheets
        gc = gspread.service_account(filename=settings.GOOGLE_SHEETS_CREDENTIALS)
        spreadsheet = gc.open('lifGPT')
        themesheet = spreadsheet.get_worksheet(0)
        sitesheet = spreadsheet.worksheet('サイト')

        file_name = request.GET.get('file_name')
        result_folder = settings.RESULT_FOLDER
        file_path = os.path.join(result_folder, file_name)

        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()
            match = re.search(r'★ーーー★.*?★ーーー★', file_content, re.DOTALL)
            if match:
                extracted_part = match.group(0)
                file_content = file_content.replace(extracted_part, '').strip()
                file_content = extracted_part + '\n' + file_content
                file_content = file_content.replace('★ーーー★', '')

        with open(settings.OUTPUT_JSON_PATH, 'r', encoding='utf-8') as file:
            json_data = json.load(file)

        site_url, wp_username, wp_password, category = None, None, None, None
        for matching_data in json_data:
            if file_name == matching_data['file_name']:
                site_name = matching_data['site_name']
                category = matching_data['category']
                for row in sitesheet.get_all_values()[1:]:
                    if site_name == row[0]:
                        site_url = row[1]
                        wp_username = row[2]
                        wp_password = row[3]
                        break

        if not (site_url and wp_username and wp_password and category):
            return JsonResponse({"error": "Matching data not found or incomplete"}, status=404)

        wp_url = f"{site_url}/xmlrpc.php"
        wp_client = Client(wp_url, wp_username, wp_password)

        post = WordPressPost()
        post.title = '仮記事(新着)'
        post.content = file_content
        post.terms_names = {'category': [category]}
        post.post_status = 'publish'

        wp_client.call(posts.NewPost(post))
        return JsonResponse({"message": "completed"}, status=200)
    except FileNotFoundError:
        return JsonResponse({"error": "File not found"}, status=404)
    except UnicodeDecodeError:
        return JsonResponse({"error": "Error decoding file. The file may not be in UTF-8 encoding."}, status=500)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    

def smart_convert(value):
    """
    Try to convert the value to an integer or float. If both conversions fail,
    return the value as a string.

    Parameters:
    value (str): The value to be converted.

    Returns:
    int, float, str: The converted value as an int, float, or str.

    Examples:
    >>> smart_convert("42")
    42

    >>> smart_convert("3.14")
    3.14

    >>> smart_convert("hello")
    'hello'

    >>> smart_convert("")
    ''
    """
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value