from django.urls import path

from matches.views import get_match_slots_ajax, show_create_match, show_join_match, show_matches

app_name = "matches"

urlpatterns = [
    path("", show_matches, name="show_matches"),
    path("create/", show_create_match, name="show_create_match"),
    path("join/<int:match_id>/", show_join_match, name="show_join_match"),
    path("get_slots/<int:field_id>/", get_match_slots_ajax, name="get_match_slots_ajax"),
]
