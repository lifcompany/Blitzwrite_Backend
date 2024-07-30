import requests
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from .serializers import SuggestKeywordSerializer

from rest_framework import status
from .models import MainKeyword, SuggestedKeyword
from sitesetting.models import LifVersion

from .models import UserProfile
from openai import OpenAI
import os
import json
from django.utils.timezone import now
import datetime
import gspread
import re

from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods import posts
from wordpress_xmlrpc.exceptions import InvalidCredentialsError, ServerConnectionError

class Base:
    stop_execution=False,
    status=""

client = OpenAI(    
        api_key=os.getenv("OPENAI_API_KEY")
)
    
def check_wordpress_access(site_url, wp_username, wp_password):
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
        return False, f"予期せぬエラーが発生しました: {e}"

def send_Notification_email(email):

    html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Generated Articles</title>
        <style>
            body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
            }
            .container {
            width: 100%;
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            overflow: hidden;
            }
            .header {
            background-color: #00bda5;
            color: #ffffff;
            padding: 20px;
            text-align: center;
            }
            .header h1 {
            margin: 0;
            }
            .content {
            padding: 20px;
            }
            .content h2 {
            color: #3a536d;
            font-size: 24px;
            }
            .content p {
            color: #555555;
            font-size: 16px;
            line-height: 1.5;
            }
            .footer {
            background-color: #f4f4f4;
            color: #888888;
            text-align: center;
            padding: 10px;
            font-size: 12px;
            }
            .footer a {
            color: #00bda5;
            text-decoration: none;
            }
            .button {
            display: inline-block;
            padding: 10px 20px;
            margin: 20px 0;
            background-color: #00bda5;
            color: #ffffff !important;
            text-decoration: none;
            border-radius: 5px;
            }
        </style>
        </head>
        <body>
        <div class="container">
            <div class="header">
            <h1>Blitzwrite</h1>
            </div>
            <div class="content">
            <h2>Welcome, </h2>
            <p>
                Thank you for registering with Blitzwrite. Please verify your email address to complete your registration and activate your account.
            </p>
            <p>
                Genreted 10/6
            </p>

            <p>
                Best regards,<br>
                The Support Team
            </p>
            </div>
            <div class="footer">
            <p>
                &copy; 2024 株式会社LIF. All rights reserved.
            </p>
            <p>
                <a href="#">Unsubscribe</a> | <a href="#">Privacy Policy</a>
            </p>
            </div>
        </div>
        </body>
        </html>
        """
    # html_content = html_content.replace("{{ verification_link }}", verification_link)
    message = Mail(
    from_email='santabaner1223@gmail.com',
    to_emails=email,
    subject='Generated Article',
    html_content=html_content
    )
    try:
        sg = SendGridAPIClient('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')
        response = sg.send(message)
        print("successfull", response.status_code)  # Print the status code
        if response.status_code == 202:
            print("Email sent successfully!")
            return {"status": "success", "status_code": response.status_code}
        else:
            print(f"Failed to send email. Status code: {response.status_code}")
            return {"status": "failure", "status_code": response.status_code}
    except Exception as e:
        print(e)
        return {"status": "error", "message": str(e)}


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


class KeywordSuggest(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def post(self, request):
        suggestions = []

        keyword_text = request.data.get('keyword', '')
        print(keyword_text)
        if not keyword_text:
            return JsonResponse({'error': 'Keyword is required.'}, status=400)

        try:
            google_ads_client = GoogleAdsClient.load_from_storage(settings.GOOGLE_ADS_YAML_PATH)
            keyword_plan_idea_service = google_ads_client.get_service("KeywordPlanIdeaService")

            keywordrequest = google_ads_client.get_type("GenerateKeywordIdeasRequest")
            keywordrequest.customer_id = settings.GOOGLE_ADS_CUSTOMER_ID
            keywordrequest.language = google_ads_client.get_service("GoogleAdsService").language_constant_path('1005')
            keywordrequest.keyword_seed.keywords.append(keyword_text)

            response = keyword_plan_idea_service.generate_keyword_ideas(request=keywordrequest)
            suggestions = []
            for result in response.results:
                keyword = result.text
                avg_monthly_searches = result.keyword_idea_metrics.avg_monthly_searches
                suggestions.append({
                    'keyword': keyword,
                    'avg_monthly_searches': avg_monthly_searches
                })
                
            return JsonResponse({'suggestions': suggestions})

        except GoogleAdsException as ex:
            return JsonResponse({'error': str(ex)}, status=400)

    
class SendNotificationEmail(APIView):
    def get(self, request):
        email=request.user.email
        print(email)

        if not email:
            return JsonResponse({'error': 'User is required.'}, status=400)

        try:
            response = send_Notification_email(email)
            if response["status"] == "success":
                return Response(
                    {
                        "success": "通知を送信しました。"
                    },
                    status=status.HTTP_201_CREATED,
                )
            elif response["status"] == "failure":
                return Response(
                    {
                        "error": "通知の送信に失敗しました。",
                        "details": response
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            else:
                return Response(
                    {"error": "メールサーバー側のエラーのため通知を送信できません。"
                    "後ほど再試行してください。",
                    "details": response 
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except GoogleAdsException as ex:
            return JsonResponse({'error': str(ex)}, status=400)

class SaveKeywords(APIView):
    def post(self, request):
        try:
            keywords_to_save = request.data.get('keywords', [])
            main_keyword_text = request.data.get('main_keyword', '')

            user = request.user 
            print(user, keywords_to_save, main_keyword_text)

            # Get or create the main keyword
            main_keyword, created = MainKeyword.objects.get_or_create(user=user, keyword=main_keyword_text)

            if not created:
                main_keyword.created_at = now()
                main_keyword.save()

                # Delete existing suggested keywords for the main keyword
                SuggestedKeyword.objects.filter(main_keyword=main_keyword).delete()

            # Prepare new keyword data for serialization
            serialized_keywords = []
            for keyword_data in keywords_to_save:
                serialized_keywords.append({
                    'main_keyword': main_keyword.id, 
                    'keyword': keyword_data.get('keyword', ''),
                    'volume': keyword_data.get('volume', 0)
                })
            print(serialized_keywords)

            # Serialize and save the new keywords
            serializer = SuggestKeywordSerializer(data=serialized_keywords, many=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def smart_convert(value):
    try:
        return eval(value)
    except:
        return value

class CreateHeading(APIView):
    def post(self, request):
        try:
            user = request.user
            user_profile = UserProfile.objects.get(user=user)
            if not user.is_premium and user_profile.credits <= 0:
                return JsonResponse({'error': 'You have no credits left to create an article.'}, status=403)

            keywords = request.data.get('keywords', [])
            versionName = request.data.get('versionName')
            
            if not keywords:
                return JsonResponse({'error': 'Keywords are required.'}, status=400)

            if versionName:
                try:
                    model = LifVersion.objects.get(model_name=versionName)
                    print("model", model)
                except LifVersion.DoesNotExist:
                    
                    return JsonResponse({'error': 'Invalid versionName'}, status=400)

                model_name = model.model_name
                endpoint = model.endpoint
                params = model.params
                param_lines = [item.strip() for item in params.replace('\n', ',').split(',') if item.strip()]
                parameters = {}
                for line in param_lines:
                    key, value = line.split('=')
                    parameters[key.strip()] = value.strip()
                     
                parameters = {k: smart_convert(v) for k, v in parameters.items()}
                if params == "" and endpoint == "https://api.openai.com/v1/chat/completions":
                    parameters = {
                        "temperature": 0.2,
                        "max_tokens": 500,
                        "frequency_penalty": 0.0,
                        'timeout': 1200
                    }
                
                responses = []
                conversation_history = [{"role": "system", "content": "You are a helpful assistant."}]
                for keyword in keywords:
                    prompt = f"I am going to write an article with the keyword 「{keyword['keyword']}」. Please write the one title of the article."
  
                    if endpoint == "https://api.openai.com/v1/chat/completions":
                        conversation_history.append({"role": "user", "content": prompt})
                    else:
                        conversation_history = prompt
                    print("conversation_history",model_name, conversation_history, parameters)
                    if endpoint == "https://api.openai.com/v1/chat/completions":
                        response = client.chat.completions.create(
                            model= model_name,
                            messages=conversation_history,
                            **parameters
                        )
                        print(response.choices[0].message.content)
                        generated_title = response.choices[0].message.content
                    
                    else:
                        response = client.completions.create(
                            model= model_name,
                            prompt=conversation_history,
                            **parameters
                        )
                        generated_title = response.choices[0].text                    
                    responses.append(generated_title.strip())

                if not user.is_premium:
                    user_profile.credits -= 1
                    user_profile.save()
                return JsonResponse({'title': responses})
            
            else:
                return JsonResponse({'error': 'GPTモデルを選択していないか、選択したモデルが正しくありません。'}, status=400)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class CreateConfig(APIView):
    def post(self, request):
        try:
            user = request.user
            user_profile = UserProfile.objects.get(user=user)
            if not user.is_premium and user_profile.credits <= 0:
                return JsonResponse({'error': 'You have no credits left to create an article.'}, status=403)

            keywords = request.data.get('keywords', [])
            versionName = request.data.get('versionName')
            
            if not keywords:
                return JsonResponse({'error': 'Keywords are required.'}, status=400)

            if versionName:
                try:
                    model = LifVersion.objects.get(model_name=versionName)
                    print("model", model)
                except LifVersion.DoesNotExist:
                    
                    return JsonResponse({'error': 'Invalid versionName'}, status=400)

                model_name = model.model_name
                endpoint = model.endpoint
                params = model.params
                param_lines = [item.strip() for item in params.replace('\n', ',').split(',') if item.strip()]
                parameters = {}
                for line in param_lines:
                    key, value = line.split('=')
                    parameters[key.strip()] = value.strip()
                     
                parameters = {k: smart_convert(v) for k, v in parameters.items()}
                if params == "" and endpoint == "https://api.openai.com/v1/chat/completions":
                    
                    print(model_name, endpoint, keywords)
                    parameters = {
                        "temperature": 0.2,
                        "max_tokens": 500,
                        "frequency_penalty": 0.0,
                        'timeout': 1200
                    }
                
                responses = []
                for keyword in keywords:
                    conversation_history = [{"role": "system", "content": "You are a helpful assistant."}]
                    prompt = f"Please provide titles so that articles can be created using the keyword 「{keyword['keyword']}」. Please use H tags to distinguish the titles. please create the titles as the array data. And  Please write in the same configuration as next.'<h2>1. タイトル</h2> <h3>1.1 タイトル</h3> <h3>1.2 タイトル</h3> <h3>1.3 タイトル</h3> <h3>1.4 タイトル</h3> <h3>1.5イトル</h3> <h2>2. タイトル</h2> <h3>2.1 タイトル</h3> <h3>2.2 タイトル</h3> <h3>2.3 タイトル</h3> <h3>2.4 タイトル</h3> <h3>2.5タイトル</h3> <h3>2.6 タイトル</h3>'. I need only array data."
                    print(prompt)
                    
                    if endpoint == "https://api.openai.com/v1/chat/completions":
                        conversation_history.append({"role": "user", "content": prompt})
                    else:
                        conversation_history = prompt
                    print("conversation_history", conversation_history, parameters)
                    if endpoint == "https://api.openai.com/v1/chat/completions":
                        response = client.chat.completions.create(
                            model= model_name,
                            messages=conversation_history,
                            **parameters
                        )
                        print(response.choices[0].message.content)
                        generated_title = response.choices[0].message.content
                    
                    else:
                        response = client.completions.create(
                            model= model_name,
                            prompt=conversation_history,
                            **parameters
                        )
                        generated_title = response.choices[0].text
                     
                    def extract_list_from_string(text):
                        list_regex = re.compile(r'\[\s*(".*?"(?:,\s*".*?")*)\s*\]', re.DOTALL)
                        match = list_regex.search(text)
                        
                        if match:
                            list_string = match.group(1)
                            list_string = list_string.replace('\\"', '"')
                            list_items = re.findall(r'"(.*?)"', list_string)
                            
                            return list_items
                        else:
                            return None   
                        
                    extracted_list = extract_list_from_string(generated_title)
                    print("ssssssssssssssssssssss", extracted_list)
                
                    responses.append(extracted_list)
                if not user.is_premium:
                    user_profile.credits -= 1
                    user_profile.save()

                return JsonResponse({'config': responses})
            
            else:
                return JsonResponse({'error': 'GPTモデルを選択していないか、選択したモデルが正しくありません。'}, status=400)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class CreateArticle(APIView):
    def post(self, request):
        try:
            user = request.user
            user_profile = UserProfile.objects.get(user=user)
            if not user.is_premium and user_profile.credits <= 0:
                return JsonResponse({'error': 'You have no credits left to create an article.'}, status=403)

            keywordconfigs = request.data.get('keywordconfigs', [])
            versionName = request.data.get('versionName')
            upload_info =request.data.get('upload_info')
            wp_url=upload_info["site_url"]
            wp_admin=upload_info["admin"]
            wp_password=upload_info["password"]
            
            
            if not wp_url or not wp_admin or not wp_password:
                return Response({'error': 'サイトのURLと管理者のログイン情報を正確に入力してください。'}, status=status.HTTP_400_BAD_REQUEST)

            access_granted, access_message = check_wordpress_access(wp_url, wp_admin, wp_password)
            if not access_granted:
                return Response({'error': access_message}, status=status.HTTP_403_FORBIDDEN)

            if versionName:
                try:
                    model = LifVersion.objects.get(model_name=versionName)
                    print("model", model)
                except LifVersion.DoesNotExist:
                    
                    return JsonResponse({'error': 'Invalid versionName'}, status=400)

                model_name = model.model_name
                endpoint = model.endpoint
                params = model.params
                param_lines = [item.strip() for item in params.replace('\n', ',').split(',') if item.strip()]
                parameters = {}
                for line in param_lines:
                    key, value = line.split('=')
                    parameters[key.strip()] = value.strip()
                     
                parameters = {k: smart_convert(v) for k, v in parameters.items()}
                if params == "" and endpoint == "https://api.openai.com/v1/chat/completions":
                    
                    parameters = {
                        "temperature": 0.2,
                        "max_tokens": 500,
                        "frequency_penalty": 0.0,
                        'timeout': 1200
                    }
                    
                gc = gspread.service_account(filename='cred.json')
                spreadsheet = gc.open('lifGPT')                  
                def get_prompt():
                    prompt_sheet = spreadsheet.worksheet('プロンプト') 
                    results = []
                    for row in prompt_sheet.get_all_values():
                        text_b = row[0]  
                        if text_b:
                            results.append(text_b)

                    return results
                prompt_data = get_prompt()
                responses = []
                return_response = []
                response=None
                filename = 'output.json' 
                
                try:
                    if os.path.exists(filename) and os.path.getsize(filename) > 0:
                        with open(filename, 'r', encoding='utf-8') as file:
                            match_results = json.load(file)
                    else:
                        match_results = []
                except json.JSONDecodeError:
                    match_results = []
                    
                print("llllllllllllllllllllllll", keywordconfigs)
                for keywordconfig in keywordconfigs:
                    text_a = keywordconfig  
                  
                    current_time = datetime.datetime.now()
                    run_directory_datetime = current_time.strftime("%Y-%m-%d-%H-%M-%S")
                    formatted_datetime = current_time.strftime("%Y/%m/%d-%H:%M")
                    print(formatted_datetime)
                
                    responses = []
                    conversation_history = [{"role": "system", "content": "You are a helpful assistant."}]
                    
                    for row, prompt_text in enumerate(prompt_data, start=1):
                        if text_a and "〇〇〇〇" in prompt_text:
                            prompt_text = prompt_text.replace("〇〇〇〇", text_a) 
                        else:
                            prompt_text = f"「{text_a}」 {prompt_text}"

                        if endpoint == "https://api.openai.com/v1/chat/completions":
                            conversation_history.append({"role": "user", "content": prompt_text})
                        else:
                            conversation_history = prompt_text
                        if endpoint == "https://api.openai.com/v1/chat/completions":
                            response = client.chat.completions.create(
                                model= model_name,
                                messages=conversation_history,
                                **parameters
                            )
                            generated_title = response.choices[0].message.content
                            
                        else:
                            response = client.completions.create(
                                model= model_name,
                                prompt=conversation_history,
                                **parameters
                            )
                            generated_title = response.choices[0].text
                            
                        if endpoint == "https://api.openai.com/v1/chat/completions":
                            responses.append(response.choices[0].message.content.strip())
                        else:
                            responses.append(response.choices[0].text)
                            
                        print("GGGGGGGGGGGGGGGGGG", responses)
                        
                    
                    with open(f'./result/{run_directory_datetime}.txt', 'w', encoding='utf-8') as file:
                        file.write('\n'.join(responses))
                        
                    
                    new_data = {
                        "file_name":f'{run_directory_datetime}.txt',
                        "site_url":upload_info["site_url"],
                        "admin" : upload_info["admin"],
                        "password" : upload_info["password"],
                        "category" : upload_info["category"],
                    }
                    print("2222222222222222222222222222222222222222222222222222222", new_data)

                    match_results.append(new_data)
                    
                    def post_article(new_data):
                        file_name =new_data['file_name']            
                        print(file_name)
                        result_folder = './result'
                        file_path = os.path.join(result_folder, file_name)
                        with open(file_path, 'r', encoding='utf-8') as file:
                            file_content = file.read()
                            match = re.search(r'★ーーー★.*?★ーーー★', file_content, re.DOTALL)
                            if match:
                                extracted_part = match.group(0)
                                file_content = file_content.replace(extracted_part, '').strip()
                                file_content = extracted_part + '\n' + file_content
                                file_content = file_content.replace('★ーーー★', '')

                        return_response.append(file_content)
 
                        site_url = new_data['site_url']
                        wp_username = new_data['admin']
                        wp_password = new_data['password']
                        category = new_data.get('category', 'Temporary Article') or 'Temporary Article'
   
                        wp_url = f"{site_url}/xmlrpc.php"
                        wp_client = Client(wp_url, wp_username, wp_password)

                        post = WordPressPost()
                        post.title = '仮記事(新着)'
                        post.content = file_content
                        post.terms_names = {
                        'category': [category]
                        }
                        post.post_status = 'draft'
                        wp_client.call(posts.NewPost(post))
                        print("completed")
                        return "completed"
                        
                    post_result=post_article(new_data)
                    print("RRRRRRRRRRRRRRRRRR", post_result)
                    Base.status=post_result

                if not user.is_premium:
                    user_profile.credits -= 1
                    user_profile.save()
                print("444444444444444", return_response)
                return JsonResponse({'config': return_response})
            
            else:
                return JsonResponse({'error': 'GPTモデルを選択していないか、選択したモデルが正しくありません。'}, status=400)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class GetUserCredit(APIView):
    def get(self, request):
        user_profile = request.user.userprofile
        data = {
            'credits': user_profile.credits,
            'is_premium': request.user.is_premium,
            'email': request.user.email
        }
        return JsonResponse(data)
    
class GetKeywordData(APIView):
    def get(self, request):
        user = request.user
        try:
            # Retrieve the most recent main keyword for the user
            main_keyword = MainKeyword.objects.filter(user=user).latest('created_at').keyword
            main_keyword_id = MainKeyword.objects.filter(user=user).latest('created_at').id
            suggest_keyword =SuggestedKeyword.objects.filter(main_keyword_id=main_keyword_id).values_list('keyword', flat=True)
            
            print(main_keyword, suggest_keyword)
            return JsonResponse({'mainkeyword': main_keyword, "suggest_keyword": list(suggest_keyword)})
        except MainKeyword.DoesNotExist:
            return JsonResponse({'error': 'You have no Data'}, status=400)
    
    