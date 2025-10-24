from django.urls import path
from tournament.views import tournament_list, tournament_detail, tournament_matches, get_tournaments_json, create_tournament, edit_tournament, delete_tournament, create_match, edit_match, delete_match, get_matches_json, join_tournament

app_name = 'tournament'

urlpatterns = [
    path('', tournament_list, name='tournament_list'),
    path('<int:pk>/', tournament_detail, name='tournament_detail'),
    path('<int:pk>/matches/', tournament_matches, name='tournament_matches'),
    path('json/', get_tournaments_json, name='get_tournaments_json'),
    path('create/', create_tournament, name='create_tournament'),
    path('<int:pk>/edit/', edit_tournament, name='edit_tournament'),
    path('<int:pk>/delete/', delete_tournament, name='delete_tournament'),
    path('<int:pk>/create_match/', create_match, name='create_match'),
    path('api/<int:pk>/matches/', get_matches_json, name='get_matches_json'),
    path('<int:pk>/join/', join_tournament, name='join_tournament'),
    path('<int:pk>/matches/<int:match_id>/edit/', edit_match, name='edit_match'),
    path('<int:pk>/matches/<int:match_id>/delete/', delete_match, name='delete_match'),
]