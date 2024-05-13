import os
import requests
from django.http import JsonResponse
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
    email_params = {
        "apikey": os.getenv("MAIL_KEY"),
        "from": "shiraishi.dev116@gmail.com",
        "to": email,
        "subject": "Email Verify - lif-post Account",
        "body": f"{content}",
        "isTransactional": True,
    }

    response = requests.post(
        "https://api.elasticemail.com/v2/email/send",
        data=email_params,
    )
    return response

class GetFileList(APIView):
    def get_file_list(request):
        directory = './result'
        
        # Retrieve file list from the directory
        file_list = os.listdir(directory)
        file_list.sort(key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=False)
        
        print(file_list)
        
        # Return the file list as JSON response
        return JsonResponse({'file_list': file_list})

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

        return Response("User saved successfully", status=status.HTTP_200_OK)
