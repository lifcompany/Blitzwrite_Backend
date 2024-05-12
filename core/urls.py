from django.urls import path
from .views import LoginView, RegisterView, GoogleRegister, GetUserView, MailVerifyView, ForgetPasswordView, ResetPasswordView, loginWithGoogle, GetUserInfo

urlpatterns = [
    path("get_file_list/", view=LoginView.as_view(), name="login"),
    path("get_model_list/", view=RegisterView.as_view(), name="register"),
    path("add_new_version/", view=GoogleRegister.as_view(), name="googleregister"),
    path("get_edit_version/", view=MailVerifyView.as_view(), name="mailverify"),
    path("delete_model/", view=ForgetPasswordView.as_view(), name="forgetpassword"),
    path("delete_files/", view=ResetPasswordView.as_view(), name="resetpassword"),
    path("get_file_content/", view=GetUserView.as_view(), name="getUserInfo"),
    path("post_article/", view=GetUserInfo.as_view(), name="getUserInfoData"),
    path("run_script/", view=GetUserInfo.as_view(), name="getUserInfoData"),
    path("stop_script/", view=loginWithGoogle.as_view(), name="loginWithGoogle"),
    path("/download/<filename>/", view=GetUserInfo.as_view(), name="downloadfile"),
]
