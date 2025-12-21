from django.urls import path
from main.views import search_fields, search_matches, show_main

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("search_fields/", search_fields, name="search_fields"),
    path("search_matches/", search_matches, name="search_matches"),
]
