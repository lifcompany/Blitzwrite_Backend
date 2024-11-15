import os
import json
import re
import datetime
import gspread
import stripe
from django.shortcuts import render, get_object_or_404
from django.http import FileResponse, Http404, JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from openai import OpenAI
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from oauth2client.service_account import ServiceAccountCredentials
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods import posts
from django.utils.decorators import method_decorator
from rest_framework.permissions import IsAuthenticated
from .models import LifVersion, SiteData
from .serializers import SiteDataSerializer, LifVersionSerializer

from django.views.decorators.http import require_http_methods
import requests
from bs4 import BeautifulSoup

from wordpress_xmlrpc.exceptions import InvalidCredentialsError, ServerConnectionError

import collections
if not hasattr(collections, 'Iterable'):
    import collections.abc
    collections.Iterable = collections.abc.Iterable

class Base:
    stop_execution = False

client = OpenAI(api_key=settings.OPENAI_API_KEY)
print(settings.OPENAI_API_KEY)
print(settings.BASE_DIR)


def check_wordpress_access(site_url, wp_username, wp_password):
    print("check wordpress access")
    try:
        wp_url = f"{site_url}/xmlrpc.php"
        wp_client = Client(wp_url, wp_username, wp_password)
        wp_client.call(posts.GetPosts({'number': 1}))
        return True, "Access granted"
    except InvalidCredentialsError:
        return False, "認証情報が無効です。ユーザー名とパスワードを確認してください。"
    except ServerConnectionError:
        return False, "WordPressサーバーに接続できません。サイトのURLを確認してください。"
    except Exception as e:
        print(e)
        return False, f"連結に失敗しました！後で再試行してください。{e}"

def get_file_list(request):
    directory = './result'
    file_list = os.listdir(directory)
    file_list.sort(key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=False)
    print(file_list)
    return JsonResponse(file_list, safe=False)


class GetModel(APIView):
    def get(self, request):
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
        user_email = request.user.email
        try:
            user_email = request.user.email
            site_data_list = SiteData.objects.filter(email=user_email)
            if not site_data_list.exists():
                return Response({"error": "Site data not found"}, status=status.HTTP_404_NOT_FOUND)
            return Response({'site_data': list(site_data_list.values())}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# def get_model_list(request):
#     models = LifVersion.objects.all()
#     model_list = []
#     for model in models:
#         model_dict = {
#             'id': model.id,
#             'display_name': model.display_name,
#             'model_name': model.model_name,
#             'endpoint': model.endpoint,
#             'params': model.params,
#         }
#         model_list.append(model_dict)
    
#     return JsonResponse(model_list, safe=False)



# @method_decorator(csrf_exempt, name='dispatch')
# @require_POST

class AddNewVersionView(APIView):
    def post(self, request):
        data = JSONParser().parse(request)
        editversion_id = data.get('editversionID')
        display_name = data.get('display_name')
        model_name = data.get('model_name')

        if not display_name or not model_name or not data.get('endpoint') or not data.get('params'):
            return JsonResponse({"error": "Missing data"}, status=400)

        try:
            if editversion_id:
                lif_version = get_object_or_404(LifVersion, id=editversion_id)
                if (LifVersion.objects.filter(display_name=display_name).exclude(id=editversion_id).exists() or
                        LifVersion.objects.filter(model_name=model_name).exclude(id=editversion_id).exists()):
                    return JsonResponse({"error": "A model with the same display name or model name already exists."}, status=409)
                
                serializer = LifVersionSerializer(lif_version, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return JsonResponse({"message": "Model updated successfully"}, status=200)
                return JsonResponse(serializer.errors, status=400)
            else:
                if LifVersion.objects.filter(display_name=display_name).exists() or LifVersion.objects.filter(model_name=model_name).exists():
                    return JsonResponse({"error": "A model with the same display name or model name already exists."}, status=409)
                
                serializer = LifVersionSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    return JsonResponse({"message": "Model added successfully"}, status=201)
                return JsonResponse(serializer.errors, status=400)
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        


@csrf_exempt 
def add_new_version(request):
    if request.method == 'POST':
        try:
            data = JSONParser().parse(request)
            model_name = data['model_name']
            endpoint = data['endpoint']
            params = data['params']

            if not all([model_name, endpoint]):
                return JsonResponse({'error': 'Missing required data'}, status=400)
            
            try:
                model_version = LifVersion.objects.get(model_name=model_name)
                model_version.endpoint = endpoint
                model_version.params = params
                model_version.save()
                message = "Model updated successfully"

            except LifVersion.DoesNotExist:
                # Create new model version
                LifVersion.objects.create(
                    model_name=model_name,
                    endpoint=endpoint,
                    params=params
                )
                message = "Model added successfully"


            # if model_name:
            #     try:
            #         model_version = LifVersion.objects.get(model_name = model_name)
            #     except LifVersion.DoesNotExist:
            #         return JsonResponse({'error': 'Model version not found'}, status=404)

            #     # Update existing model version
            #     model_version.model_name = model_name
            #     model_version.endpoint = endpoint
            #     model_version.params = params
            #     model_version.save()
            #     message = "Model updated successfully"
            # else:

            #     if LifVersion.objects.filter(model_name=model_name).exists():
            #         return JsonResponse({'error': 'A model with the same model name already exists.'}, status=409)

            #     # Create new model version
            #     LifVersion.objects.create(
            #         model_name=model_name,
            #         endpoint=endpoint,
            #         params=params
            #     )
            #     message = "Model added successfully"

            return JsonResponse({'message': message}, status=201)

        except KeyError as e:

            return JsonResponse({'error': f"Missing data: {str(e)}"}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            print("This is add new version")
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt 
def update_model(request):
    if request.method == 'POST':
        try:
            data = JSONParser().parse(request)
            model_name = data['model_name']
            endpoint = data['endpoint']
            params = data['params']

            if not all([model_name, endpoint]):
                return JsonResponse({'error': 'Missing required data'}, status=400)
            
            try:
                model_version = LifVersion.objects.get(model_name=model_name)
                model_version.endpoint = endpoint
                model_version.params = params
                model_version.save()
                message = "Model updated successfully"

            except LifVersion.DoesNotExist:
                # Create new model version
                LifVersion.objects.create(
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
            print("This is add new version")
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt 
def get_edit_version(request):
    if request.method == 'POST':
        try:
            data = JSONParser().parse(request)
            editModelName = data['editModalName']
            print(editModelName)


            if editModelName:
                try:
                    edit_model = LifVersion.objects.get(model_name=editModelName)
                    model_data = {
                        "display_name": edit_model.display_name,
                        "model_name": edit_model.model_name,
                        "endpoint": edit_model.endpoint,
                        "params": edit_model.params,
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
    return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt 
def delete_model(request):
    try:
        data = JSONParser().parse(request)
        delete_model_name = data['model_name']
        if delete_model_name:
            try:
                model_version = LifVersion.objects.get(model_name=delete_model_name)
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

@method_decorator(csrf_exempt, name='dispatch')
def run_script(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        version_id = data.get('versionId')
        if version_id:
            try:
                model = LifVersion.objects.get(id=version_id)
            except LifVersion.DoesNotExist:
                return JsonResponse({'error': 'Invalid versionId'}, status=400)

            display_name = model.display_name
            model_name = model.model_name
            endpoint = model.endpoint
            params = model.params
            param_lines = [item.strip() for item in params.replace('\n', ',').split(',') if item.strip()]

            parameters = {}
            for line in param_lines:
                key, value = line.split('=')
                parameters[key.strip()] = value.strip()

            parameters = {k: smart_convert(v) for k, v in parameters.items()}
            if not params and endpoint == "https://api.openai.com/v1/chat/completions":
                parameters = {
                    "temperature": 0.2,
                    "max_tokens": 500,
                    "frequency_penalty": 0.0,
                    'timeout': 1200
                }

            # Google Sheets and external API processing
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            creds = ServiceAccountCredentials.from_service_account_file('cred.json', scopes=scope)
            gc = gspread.service_account(filename='cred.json')
            spreadsheet = gc.open('lifGPT')
            worksheet = spreadsheet.get_worksheet(0)

            def process_bbb_data():
                bbb_ws = spreadsheet.worksheet('プロンプト')
                results = [row[0] for row in bbb_ws.get_all_values() if row[0]]
                return results

            bbb_results = process_bbb_data()
            print(bbb_results)
            responses = []
            response = None
            new_file_list = []
            filename = 'output.json'
            match_results = []

            if os.path.exists(filename) and os.path.getsize(filename) > 0:
                with open(filename, 'r', encoding='utf-8') as file:
                    match_results = json.load(file)

            for row_number, row in enumerate(worksheet.get_all_values()[1:], start=2):
                text_a = row[0]
                status_c = row[1]
                site_name = row[2]
                category = row[3]
                if not status_c:
                    current_time = datetime.datetime.now()
                    run_directory_datetime = current_time.strftime("%Y-%m-%d-%H-%M-%S")
                    formatted_datetime = current_time.strftime("%Y/%m/%d-%H:%M")

                    responses = []
                    conversation_history = [{"role": "system", "content": "You are a helpful assistant."}]
                    for row, text_prompt in enumerate(bbb_results, start=1):
                        if text_a and "〇〇〇〇" in text_prompt:
                            text_prompt = text_prompt.replace("〇〇〇〇", text_a)
                        else:
                            text_prompt = f"「{text_a}」 {text_prompt}"

                        if endpoint == "https://api.openai.com/v1/chat/completions":
                            conversation_history.append({"role": "user", "content": text_prompt})
                        else:
                            conversation_history = text_prompt

                        if endpoint == "https://api.openai.com/v1/chat/completions":
                            response = client.chat.completions.create(
                                model=f"{model_name}",
                                messages=conversation_history,
                                **parameters
                            )
                            responses.append(response.choices[0].message.content.strip())
                        else:
                            response = client.completions.create(
                                model=f"{model_name}",
                                prompt=conversation_history,
                                **parameters
                            )
                            responses.append(response.choices[0].text.strip())

                    with open(f'./result/{run_directory_datetime}.txt', 'w', encoding='utf-8') as file:
                        file.write('\n'.join(responses))
                    new_data = {
                        "file_name": f'{run_directory_datetime}.txt',
                        "site_name": site_name,
                        "category": category
                    }
                    match_results.append(new_data)
                    new_file_list.append(f'{run_directory_datetime}.txt')

                    def post_article(new_data):
                        gc = gspread.service_account(filename='cred.json')
                        spreadsheet = gc.open('lifGPT')  
                        sitesheet = spreadsheet.worksheet('サイト') 
                        site_name = new_data['site_name']
                        category = new_data['category']
                        for row in sitesheet.get_all_values()[1:]:
                            if site_name == row[0]:
                                site_url = row[1]
                                wp_username = row[2]
                                wp_password = row[3]
                                wp_url = f"{site_url}/xmlrpc.php"
                                wp_client = Client(wp_url, wp_username, wp_password)

                                file_name = new_data['file_name']
                                file_path = os.path.join('./result', file_name)
                                with open(file_path, 'r', encoding='utf-8') as file:
                                    file_content = file.read()
                                    match = re.search(r'★ーーー★.*?★ーーー★', file_content, re.DOTALL)
                                    if match:
                                        extracted_part = match.group(0)
                                        file_content = file_content.replace(extracted_part, '').strip()
                                        file_content = extracted_part + '\n' + file_content
                                        file_content = file_content.replace('★ーーー★', '')

                                post = WordPressPost()
                                post.title = '仮記事(新着)'
                                post.content = file_content
                                post.terms_names = {
                                    'category': [category]
                                }
                                post.post_status = 'draft'
                                wp_client.call(posts.NewPost(post))
                                worksheet.update('B' + str(row_number), formatted_datetime)
                                return "completed"

                    post_article(new_data)

            data = {
                'status': "completed",
                'list': new_file_list
            }
            return JsonResponse(data)

        else:
            return JsonResponse({'error': 'Invalid versionId format'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
def stop_script(request):
    if request.method == 'POST':
        Base.stop_execution = True
        return JsonResponse({"message": "Stopped"})
    return JsonResponse({"error": "Invalid request method"}, status=400)

def download_text_file(request, filename):
    directory = os.path.join(settings.BASE_DIR, 'result')  # Adjust as needed
    filepath = os.path.join(directory, filename)

    if os.path.isfile(filepath):
        return FileResponse(open(filepath, 'rb'), as_attachment=True)
    else:
        raise Http404("File not found")
    
class SetSite(APIView):
    def post(self, request):
        user_email = request.user.email
        data = JSONParser().parse(request)
        data['email'] = user_email
        wp_url=data["site_url"]
        wp_admin=data["admin_name"]
        wp_password=data["admin_pass"]
        print(wp_url, wp_admin, wp_password)
        if not wp_url or not wp_admin or not wp_password:
            return Response({'error': 'サイトのURLと管理者のログイン情報を正確に入力してください。'}, status=status.HTTP_400_BAD_REQUEST)

        access_granted, access_message = check_wordpress_access(wp_url, wp_admin, wp_password)
        if not access_granted:
            return Response({'error': access_message}, status=status.HTTP_403_FORBIDDEN)

        try:
            site_data = SiteData.objects.get(site_url=data['site_url'])
            serializer = SiteDataSerializer(site_data, data=data, partial=True)
        except SiteData.DoesNotExist:
            serializer = SiteDataSerializer(data=data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetSite(APIView):
    def get(self, request):
        user_email = request.user.email
        try:
            user_email = request.user.email
            site_data_list = SiteData.objects.filter(email=user_email).order_by('-created_at')
            if not site_data_list.exists():
                return Response({"error": "Site data not found"}, status=status.HTTP_404_NOT_FOUND)
            return Response({'site_data': list(site_data_list.values())}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
def get_site_title(request):
    site_url = request.GET.get('siteUrl')
    print(site_url)
    if site_url.strip() != '':
        try:
            response = requests.get(site_url)
            response.raise_for_status()  # Raise an exception for bad responses (4xx or 5xx)

            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.title.string if soup.title else 'Title not found'

            return JsonResponse({'title': title})
        
        except requests.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Empty URL provided'}, status=400)
        
@csrf_exempt
def delete_account(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        return JsonResponse(email, status=200)
    return JsonResponse({"error": "Invalid request method"}, status=405)

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

@csrf_exempt
def create_payment_intent(request):
    if request.method == 'POST':
        try:
            intent = stripe.PaymentIntent.create(
                amount=1000,
                currency='usd',
            )
            return JsonResponse({'clientSecret': intent['client_secret']})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=403)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)
    
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET', 'DELETE', 'PATCH'])
def payment_method(request):
    print(request.user)
    if request.method == "GET":
        # retrieve current payment methods for the customer
        # usually there should only be one payment method per customer
        email = request.user.email
        print(email)
        for customer in stripe.Customer.list(email=email).data:
            for payment_method in customer.list_payment_methods(type="card").data:
                return Response({
                    "id": payment_method["id"],
                    "last4": payment_method["card"]["last4"],
                    "exp_month": payment_method["card"]["exp_month"],
                    "exp_year": payment_method["card"]["exp_year"],
                })
        else:
            return Response(None)

    elif request.method == "DELETE":
        # remove all payment methods from the customer
        email = request.user.email
        for customer in stripe.Customer.list(email=email).data:
            for payment_method in customer.list_payment_methods(type="card").data:
                stripe.PaymentMethod.detach(payment_method["id"])
        return Response(status=status.HTTP_204_NO_CONTENT)

    elif request.method == "PATCH":
        # detach all other payment methods from the customer
        # except the one specified in the request
        # essentially updating the customer's payment methods
        payment_method_id = request.query_params["id"]
        email = request.user.email
        for customer in stripe.Customer.list(email=email).data:
            for payment_method in customer.list_payment_methods(type="card").data:
                if payment_method["id"] != payment_method_id:
                    stripe.PaymentMethod.detach(payment_method["id"])
        return Response(status=status.HTTP_204_NO_CONTENT)
    else:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
def setup_intent(request):
    if request.method == 'POST':
        email = request.user.email

        # make sure we don't create a duplicate customer for the same email
        customers = stripe.Customer.list(email=email).data
        if customers:
            customer = customers[0]
        else:
            customer = stripe.Customer.create(
                email=email,
            )

        try:
            intent = stripe.SetupIntent.create(
                automatic_payment_methods={"enabled": True},
                customer=customer.id)

            return Response({
                'id': intent.id,
                'clientSecret': intent.client_secret
            })
        except stripe.error.InvalidRequestError as e:
            print(e)
            return Response("Invalid request", status=400)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)

@api_view(['POST'])
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = 'whsec_...'  # Your webhook secret
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return Response(status=400)
    except stripe.error.SignatureVerificationError as e:
        return Response(status=400)
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object'] 
    return Response(status=200)