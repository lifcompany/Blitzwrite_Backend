from django.urls import path
from .views import LoginView, RegisterView, GoogleRegister, GetUserView, MailVerifyView, ForgetPasswordView, ResetPasswordView, loginWithGoogle, GetUserInfo, DeleteUser, GoogleLoginCheck, GoogleLoginCheck2

urlpatterns = [
    path("login/", view=LoginView.as_view(), name="login"),
    path("register/", view=RegisterView.as_view(), name="register"),
    path("google-register/", view=GoogleRegister.as_view(), name="googleregister"),
    path("mail-verify/", view=MailVerifyView.as_view(), name="mailverify"),
    path("forget-password/", view=ForgetPasswordView.as_view(), name="forgetpassword"),
    path("reset-password/", view=ResetPasswordView.as_view(), name="resetpassword"),
    path("getUser/", view=GetUserView.as_view(), name="getUserInfo"),
    path("getUserInfo/", view=GetUserInfo.as_view(), name="getUserInfoData"),
    path("getUserName/", view=GetUserInfo.as_view(), name="getUserInfoData"),
    path("loginWithGoogle/", view=loginWithGoogle.as_view(), name="loginWithGoogle"),
    path("delete_account/", view=DeleteUser.as_view(), name="delete_account"),
    path("check-registration/", view=GoogleLoginCheck.as_view(), name="checkregistration"),
    path("check-google-registration/", view=GoogleLoginCheck2.as_view(), name="checkgoogleregistration")

    
]
