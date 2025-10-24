from django.urls import path

from authentication.views import show_login, show_register

app_name = "authentication"

urlpatterns = [
    path("register/", show_register, name="show_register"),
    path("login/", show_login, name="show_login"),
]
