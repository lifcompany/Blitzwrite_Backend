from django.urls import path
from .views import GetFileList, loginWithGoogle

urlpatterns = [
    path("get_file_list/", view=GetFileList.as_view(), name="get_file_list"),
    # path("get_model_list/", view=RegisterView.as_view(), name="get_model_list"),
    # path("add_new_version/", view=GoogleRegister.as_view(), name="add_new_version"),
    # path("get_edit_version/", view=MailVerifyView.as_view(), name="get_edit_version"),
    # path("delete_model/", view=ForgetPasswordView.as_view(), name="delete_model"),
    # path("delete_files/", view=ResetPasswordView.as_view(), name="delete_files"),
    # path("get_file_content/", view=GetUserView.as_view(), name="get_file_content"),
    # path("post_article/", view=GetUserInfo.as_view(), name="post_article"),
    # path("run_script/", view=GetUserInfo.as_view(), name="run_script"),
    # path("stop_script/", view=loginWithGoogle.as_view(), name="stop_script"),
    # path("/download/<filename>/", view=GetUserInfo.as_view(), name="downloadfile"),
]
