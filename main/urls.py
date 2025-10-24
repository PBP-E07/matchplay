from django.urls import path
from main.views import search_fields, show_main

urlpatterns = [
    path("", show_main, name="show_main"),
    path('search-fields/', search_fields, name='search_fields'),
]
