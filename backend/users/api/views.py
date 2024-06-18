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

from backend.users.models import User

from .serializers import UserSerializer, LoginSerializer

def send_mail(email, content):
    print(os.getenv("MAIL_KEY"))
    email_params = {
        "apikey": "",
        "from": "andresimoni1223@gmail.com",
        "to": "andresimoni1223@gmail.com",
        "subject": "Email Verify - lif-post Account",
        "body": f"{content}",
        "isTransactional": True,
    }
    headers = {
        'Content-Type': 'application/json'
    }
    print(email, content, email_params)
    response = requests.post(
        "https://api.elasticemail.com/v2/email/send",
        params=email_params,
    )
    return response


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
                            response = send_mail(
                                email,
                                f"http://127.0.0.1:3000/mail-verify/?token={str(refresh.access_token)}",
                            )
                            print(response)
                            if response.status_code == 200:
                                return Response(
                                    {
                                        "success": "ユーザーが正常に新規登録され、認証リンクが送信されました。"
                                    },
                                    status=status.HTTP_201_CREATED,
                                )
                            else:
                                return Response(
                                    {"success": "認証リンクを再送する。"},
                                    status=status.HTTP_201_CREATED,
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
        try:
            user = User.objects.get(email=email)
            refresh = RefreshToken.for_user(user)
            response = send_mail(
                email,
                f"http://127.0.0.1:3000/reset-password/?token={str(refresh.access_token)}",
            )
            if response.status_code == 200:
                return Response(
                    {"success": "認証リンクが送信されました。"},
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {"success": "Resend verification link."},
                    status=status.HTTP_201_CREATED,
                )
        except Exception as e:
            print(e)
            return Response(
                {"error": "ユーザーが存在しない"}, status=status.HTTP_400_BAD_REQUEST
            )


class ResetPasswordView(APIView):
    def post(self, request):
        user = request.user
        password = request.data["password"]
        confirm_password = request.data["confirmPassword"]
        if password == confirm_password:
            user.password = password
            user.save()
            return Response({"success": "Reset Password"}, status=status.HTTP_200_OK)
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
            print("user validated ------------------------>", serializer.validated_data)
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]
            print("user Validate data ------------------------>", email, password)
            user = authenticate(request, email=email, password=password)
            print("userEmailAddress=====>", user)
            if user is not None:
                if user.mail_verify_statu:
                    login(request, user)
                    refresh = RefreshToken.for_user(user)
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
            return Response(serializer.error_messages)


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

        # Check if the user already exists
        user, created = User.objects.get_or_create(fullname=name, email=email)
        if created:
            user.fullname = name
            user.mail_verify = True
            user.save()

        return Response("ユーザー登録成功", status=status.HTTP_200_OK)
