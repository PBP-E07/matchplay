from django.urls import path

from authentication.views import do_logout, login_json, logout_json, register_json, show_login, show_register

app_name = "authentication"

urlpatterns = [
    path("register/", show_register, name="show_register"),
    path("login/", show_login, name="show_login"),
    path("logout/", do_logout, name="do_logout"),
    path("api/login/", login_json, name="login"),
    path("api/register/", register_json, name="register"),
    path("api/logout/", logout_json, name="logout"),
]
