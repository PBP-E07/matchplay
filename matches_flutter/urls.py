from django.urls import path
from matches_flutter.views import match_list_api

app_name = "matches_flutter"

urlpatterns = [
    path("", match_list_api, name="match_list_api"),
]
