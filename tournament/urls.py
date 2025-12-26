from django.urls import path
from tournament.views import tournament_list, tournament_detail, tournament_matches, get_tournaments_json, get_tournament_teams, create_tournament, edit_tournament, delete_tournament, create_match, edit_match, delete_match, get_matches_json, join_tournament, create_tournament_api, create_match_api, join_tournament_api, edit_match_api, delete_match_api, edit_tournament_api, delete_tournament_api

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
    path('api/tournament/create/', create_tournament_api, name='api_create_tournament'),
    path('api/tournament/<int:pk>/matches/create/', create_match_api, name='api_create_match'),
    path('api/tournament/<int:pk>/teams/', get_tournament_teams, name='get_tournament_teams'),
    path('api/<int:pk>/join/', join_tournament_api, name='join_tournament_api'),
    path('api/<int:pk>/matches/<int:match_id>/edit/', edit_match_api, name='edit_match_api'),
    path('api/<int:pk>/matches/<int:match_id>/delete/', delete_match_api, name='delete_match_api'),
    path('api/edit/<int:pk>/', edit_tournament_api, name='edit_tournament_api'),
    path('api/delete/<int:pk>/', delete_tournament_api, name='delete_tournament_api'),
]