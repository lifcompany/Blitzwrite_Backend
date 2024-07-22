import os
import requests
from django.contrib.auth import authenticate, login, get_user_model
from rest_framework import status, permissions, generics
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from allauth.account.models import EmailAddress
from sitesetting.models import SiteData
from django.http import FileResponse, Http404, JsonResponse
import jwt

from backend.users.models import User
from .serializers import UserSerializer, LoginSerializer
from django.conf import settings

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_app_email(email, verification_link):
    print(verification_link)

    html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Eメール認証</title>
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
            <h2>こんにちは お客様, </h2>
            <p>
                Blitzwriteへの登録ありがとうございます。登録を完了し、アカウントを有効化するために、メールアドレスの確認を行ってください。
            </p>
            <p>
                以下のボタンをクリックしてメールアドレスを確認してください：
            </p>
            <a href="{{ verification_link }}" class="button">メールアドレスの確認</a>
            <div id=":im" class="a3s aiL "><a href="{{ verification_link }}" target="_blank">{{ verification_link }}</a><img alt="" width="1" height="1" border="0" style="height:1px!important;width:1px!important;border-width:0!important;margin-top:0!important;margin-bottom:0!important;margin-right:0!important;margin-left:0!important;padding-top:0!important;padding-bottom:0!important;padding-right:0!important;padding-left:0!important"><div class="yj6qo"></div><div class="adL">
            </div></div>
            <p>
                アカウントを作成していない場合は、このメールを無視するか、サポートチームまでご連絡ください。
            </p>
            <p>
               よろしくお願いいたします。
            </p>
            </div>
            <div class="footer">
            <p>
                &copy; 2024 株式会社LIF. All rights reserved.
            </p>
            </div>
        </div>
        </body>
        </html>
        """
    html_content = html_content.replace("{{ verification_link }}", verification_link)
    message = Mail(
    from_email='santabaner1223@gmail.com',
    to_emails=email,
    subject='Mail-verify',
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
    
def send_reset_password(email, verification_link):
    print(verification_link)

    html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Email Verification</title>
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
            <h1>Reset-Password Blitzwrite</h1>
            </div>
            <div class="content">
            <h2>こんにちは お客様,</h2>
            <p>
                パスワードリセットのリクエストを受け付けました。以下のボタンをクリックして、新しいパスワードを設定してください。
            </p>
            <a href="{{ verification_link }}" class="button">パスワードの再設定</a>
            <div id=":im" class="a3s aiL "><a href="{{ verification_link }}" target="_blank">{{ verification_link }}</a><img alt="" width="1" height="1" border="0" style="height:1px!important;width:1px!important;border-width:0!important;margin-top:0!important;margin-bottom:0!important;margin-right:0!important;margin-left:0!important;padding-top:0!important;padding-bottom:0!important;padding-right:0!important;padding-left:0!important"><div class="yj6qo"></div><div class="adL">
            </div></div>
            <p>
             このリンクは、リクエストから24時間以内にご使用ください。それ以降は無効になります。
            </p>
            <p>
                もしこのリクエストに覚えがない場合は、このメールを無視しても問題ありません。お手数ですが、何かご不明点がありましたら、サポートまでご連絡ください。<br>
                よろしくお願いいたします。
            </p>
            </div>
            <div class="footer">
            <p>
                &copy; 2024 株式会社LIF. All rights reserved.
            </p>
            </div>
        </div>
        </body>
        </html>
        """
    html_content = html_content.replace("{{ verification_link }}", verification_link)
    message = Mail(
    from_email='santabaner1223@gmail.com',
    to_emails=email,
    subject='Mail-verify',
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
class UserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "pk"

    def get_queryset(self, *args, **kwargs):
        assert isinstance(self.request.user.id, int)
        return self.queryset.filter(id=self.request.user.id)

    @action(detail=False)
    def me(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class RegisterView(APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def post(self, request):
        front_url=os.getenv("FRONT_URL")
        try:
            data = request.data
            email = data["email"]
            password = data["password"]

            if password:
                if len(password) >= 8:
                    if not User.objects.filter(email=email).exists():
                        user = User.objects.create_user(
                            email=email,
                            password=password,
                        )
                        if User.objects.filter(email=email).exists():
                            # mail verify
                            refresh = RefreshToken.for_user(user)
                            response = send_app_email(
                                email,
                                f"{front_url}/mail-verify/?token={str(refresh.access_token)}",
                            )
                            if response["status"] == "success":
                                return Response(
                                    {
                                        "success": "ユーザーが正常に新規登録され、認証リンクが送信されました。"
                                    },
                                    status=status.HTTP_201_CREATED,
                                )
                            elif response["status"] == "failure":
                                return Response(
                                    {
                                        "error": "認証リンクを送信できませんでした。",
                                        "details": response
                                    },
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                                )
                            else:
                                return Response(
                                    {"error": "メールサーバー側のエラーにより、認証コードを送信できません。"
                                    "後ほど再試行してください。",
                                    "details": response 
                                    },
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                                )
                        else:
                            return Response(
                                {"error": "ユーザーの作成に失敗しました"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            )
                    else:
                        return Response(
                            {"error": "ユーザーメールアドレスが既に存在する"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                else:
                    return Response(
                        {"error": "パスワードは8文字以上"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                return Response(
                    {"error": "パスワードが一致しない"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            print(e)
            return Response(
                {"error": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# class GoogleRegister(APIView):

User = get_user_model()
class GoogleRegister(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer # Create a serializer for user registration

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        if user:
            return Response({'message': 'ユーザー登録成功'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        user = serializer.save()
        user.is_active = True  # Activate user upon registration
        user.save()
        EmailAddress.objects.create(user=user, email=user.email, primary=True, verified=True)  # Mark email as verified
        return user
    

class MailVerifyView(APIView):
    def post(self, request):
        print("user=============>", request.user)
        user = request.user
        user.mail_verify_statu = True
        user.save()
        return Response({"success": "Email verified"}, status=status.HTTP_200_OK)


# class MailVerifyView(APIView):
#     permission_classes = (permissions.AllowAny,)

#     def post(self, request):
#         serializer = MailVerifySerializer(data=request.data)
#         if serializer.is_valid():
#             token = serializer.validated_data['token']
#             try:
#                 # refresh = RefreshToken(token)
#                 user_id = "refresh['user_id']"
#                 user = User.objects.get(id=user_id)
#                 print("11111111", user)
#                 if not user.mail_verify_statu:
#                     user.mail_verify_statu = True
#                     user.save()
#                     return Response({"message": "User successfully verified"}, status=status.HTTP_200_OK)
#                 else:
#                     return Response({"message": "User is already verified"}, status=status.HTTP_400_BAD_REQUEST)
#             except Exception as e:
#                 return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class ForgetPasswordView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def post(self, request):
        email = request.data["email"]
        front_url=os.getenv("FRONT_URL")
        print(front_url)
        try:
            user = User.objects.get(email=email)
            refresh = RefreshToken.for_user(user)
            response = send_reset_password(
                email,
                f"{front_url}/reset-password/?token={str(refresh.access_token)}",
            )
            if response["status"] == "success":
                return Response(
                    {"success": "認証リンクが送信されました。"},
                    status=status.HTTP_201_CREATED,
                )
            elif response["status"] == "failure":
                return Response(
                    {
                        "error": "認証リンクを送信できませんでした。",
                        "details": response  # Optional: Include details for debugging
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            else:
                return Response(
                    {"error": "メールサーバー側のエラーにより、認証コードを送信できません。"
                    "後ほど再試行してください。",
                    "details": response 
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except Exception as e:
            print(e)
            return Response(
                {"error": "ユーザーが存在しない"}, status=status.HTTP_400_BAD_REQUEST
            )

class ResetPasswordView(APIView):
    def post(self, request):
        email=request.user
        user = User.objects.get(email=email)
        password = request.data["password"]
        confirm_password = request.data["confirmPassword"]

        if password == confirm_password:
            user.set_password(password)
            user.save()
            return Response({"success": "success"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Password not matched"})

class LoginView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        data = request.data

        print("userValid=====>",serializer.is_valid())

        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]
            user = authenticate(request, email=email, password=password)
            if user is not None:
                if user.mail_verify_statu:
                    login(request, user)
                    refresh = RefreshToken.for_user(user)
                    print(str(refresh.access_token))
                    return Response(
                        {
                            "status": {
                                "type": "success",
                                "message": "おかえりなさい！ログインに成功しました。",
                            },
                            "result": {
                                "token": str(refresh.access_token),
                                "user": {
                                    "email": user.email,
                                    "permission": user.user_type,
                                    # Include any other user fields as needed
                                },
                            },
                            "navigate": "/home",
                        },
                    )
                else:
                    return Response(
                        {
                            "error": "Email not verified",
                        },
                        status=status.HTTP_401_UNAUTHORIZED,
                    )
            else:
                return Response(
                    {
                        "error": "無効な電子メールまたはパスワード",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {
                    "error": "ログイン失敗！もう一度お試しください",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
            # return Response(serializer.error_messages)


class GetUserView(APIView):
    def post(self, request):
        user = request.user
        print(user)
        find_user = User.objects.get(email=user)

        if find_user:
            refresh = RefreshToken.for_user(find_user)
            return Response(
                {
                    "result": {
                        "token": str(refresh.access_token),
                        "user": {
                            "username": user.fullname,
                            "email": user.email,
                            # Include any other user fields as needed
                        },
                    }
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "ユーザーが存在しません。ログインしてください。"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class GetUserInfo(APIView):
    def post(self, request):
        # Retrieve all users from the database
        all_users = User.objects.all()

        # Extract relevant information (username and email) from each user object
        users_info = [
            {"username": user.fullname, "email": user.email} for user in all_users
        ]

        return Response({"user": users_info}, status=status.HTTP_200_OK)


class loginWithGoogle(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def post(self, request):
        name = request.data.get("name")
        email = request.data.get("email")

        user, created = User.objects.get_or_create(fullname=name, email=email)
        if created:
            user.fullname = name
            user.mail_verify = True
            user.save()

        return Response("ユーザー登録成功", status=status.HTTP_200_OK)


class DeleteUser(APIView):
    def post(self, request):
        user = request.user
        email = request.data.get("email")
        print(email, user.email)
        if user.email != email:
            return Response(
                {"error": "Please input the correct Email Address。"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        del_user = User.objects.get(email=user)
        del_user_site = SiteData.objects.filter(email = user)


        if del_user:
            del_user.delete()
            del_user_site.delete()
            return Response("削除成功", status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "ユーザーが見つかりません。"},
                status=status.HTTP_400_BAD_REQUEST,
            )

class GoogleLoginCheck(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def post(self, request):
        credential = request.data.get('credential')
        print(credential)
        clientId = "412305795434-j10qukf8odkfe41d3ohmjg7rcb5lo3mm.apps.googleusercontent.com"
        if not credential:
            return JsonResponse({'error': 'Google credentials not received'}, status=400)

        try:
            header = jwt.get_unverified_header(credential)
            rsa_key = self.get_google_public_key(header['kid'])
            decoded_token = jwt.decode(credential, rsa_key, algorithms=["RS256"], audience=clientId, leeway=600)

            email = decoded_token.get('email')

            if not email:
                return JsonResponse({'error': 'Failed to extract email from Google credentials'}, status=400)
            
            is_registered = User.objects.filter(email=email).exists()
            if not is_registered:
                User.objects.create_user(email=email, password=email, mail_verify_statu=True)

            user = authenticate(request, email=email, password=email)
            if user is not None:
                refresh = RefreshToken.for_user(user)
                print(str(refresh.access_token))

            return JsonResponse(
                {
                    'message': 'Successfully authenticated with Google',
                    'accessToken':str(refresh.access_token)
                } 
            )
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token has expired'}, status=400)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Invalid token'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    def get_google_public_key(self, kid):
        # Get Google's public keys
        response = requests.get("https://www.googleapis.com/oauth2/v3/certs")
        if response.status_code != 200:
            raise ValueError("Failed to fetch Google public keys")

        keys = response.json()['keys']
        for key in keys:
            if key['kid'] == kid:
                return jwt.algorithms.RSAAlgorithm.from_jwk(key)
        raise ValueError("Key ID not found in Google's public keys")
        

class GoogleLoginCheck2(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()
         
    def post(self, request):

        access_token = request.data.get('access_token')
        token_info_url = 'https://www.googleapis.com/oauth2/v3/tokeninfo'
        params = {'access_token': access_token}
        
        try:
            response = requests.get(token_info_url, params=params)
            token_info = response.json()

            if response.status_code == 200:
                # Token is valid, proceed with your logic (e.g., register user, generate JWT token)
                # Example logic: register or authenticate the user based on token info
                email = token_info.get('email')
                # Add your logic here to register or authenticate the user
                # Example: user = User.objects.get(email=email)
                if not email:
                    return JsonResponse({'error': 'Failed to extract email from Google credentials'}, status=400)
            
                is_registered = User.objects.filter(email=email).exists()
                if not is_registered:
                    User.objects.create_user(email=email, password=email, mail_verify_statu=True)

                user = authenticate(request, email=email, password=email)
                if user is not None:
                    refresh = RefreshToken.for_user(user)
                    print(str(refresh.access_token))
                return JsonResponse(
                    {
                        'message': 'Successfully authenticated with Google',
                        'accessToken':str(refresh.access_token)
                    } 
                )
            else:
                # Token validation failed, handle the error
                return JsonResponse({'error': 'Invalid access token'}, status=401)

        except requests.exceptions.RequestException as e:
            # Handle network or server errors
            return JsonResponse({'error': f'Request failed: {e}'}, status=500)




class CheckPremiumStatus(APIView):

    def post(self, request):
        user = request.user
        if user.is_premium:
            return Response(
                {
                    "status": "is premium",
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "status": "is not premium",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class GetUserEmail(APIView):
    def get(self, request):
        user = request.user
        return JsonResponse({'email': user.email})