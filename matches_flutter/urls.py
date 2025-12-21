from django.urls import path
from matches_flutter.views import get_occupied_slots, join_match_api, match_list_api

app_name = "matches_flutter"

urlpatterns = [
    path("", match_list_api, name="match_list_api"),
    path('matches/slots/', get_occupied_slots, name='get_occupied_slots'),
    path('<int:match_id>/join/', join_match_api, name='join_match_api'),
]
