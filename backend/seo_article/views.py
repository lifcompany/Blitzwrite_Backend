import requests
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, get_user_model
from django.conf import settings

from rest_framework import status, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from seo_article.models import MainKeyword
from .serializers import SuggestKeywordSerializer


from rest_framework import status
from .models import Keyword, MainKeyword
from backend.users.models import User

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

# class SaveKeywords(APIView):
#     def post(self, request):
#         keywords_to_save = request.data.get('keywords', [])

#         serialized_keywords = []
#         for keyword_data in keywords_to_save:
#             print("1111111", keyword_data.get('volume', 0) )
            
#             serialized_keywords.append({
#                 'name': keyword_data.get('keyword', ''),
#                 'volume': keyword_data.get('volume', 0)  # Adjust as per your model field name
#             })
#         serializer = KeywordSerializer(data=serialized_keywords, many=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class SaveKeywords(APIView):
    def post(self, request):
        try:
            keywords_to_save = request.data.get('keywords', [])
            main_keyword_text = request.data.get('main_keyword', '')

            user = request.user 
            print(user, keywords_to_save, main_keyword_text)

            main_keyword, created = MainKeyword.objects.get_or_create(user=user, keyword=main_keyword_text)

            serialized_keywords = []
            for keyword_data in keywords_to_save:
                serialized_keywords.append({
                    'main_keyword': main_keyword.id, 
                    'keyword': keyword_data.get('keyword', ''),
                    'volume': keyword_data.get('volume', 0)
                })
            print(serialized_keywords)
            serializer = SuggestKeywordSerializer(data=serialized_keywords, many=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class CreateHeading(APIView):
    def post(self, request):
        try:
            keywords_to_save = request.data.get('keywords', [])
            main_keyword_text = request.data.get('main_keyword', '')

            user = request.user 
            print(user, keywords_to_save, main_keyword_text)

            main_keyword, created = MainKeyword.objects.get_or_create(user=user, keyword=main_keyword_text)

            serialized_keywords = []
            for keyword_data in keywords_to_save:
                serialized_keywords.append({
                    'main_keyword': main_keyword.id, 
                    'name': keyword_data.get('keyword', ''),
                    'volume': keyword_data.get('volume', 0)
                })

            serializer = SuggestKeywordSerializer(data=serialized_keywords, many=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)