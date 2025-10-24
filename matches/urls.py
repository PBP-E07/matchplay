from django.urls import path
from . import views

app_name = 'matches'

urlpatterns = [
    path('', views.match_list_view, name='match_list'),
    path('create/', views.create_match_view, name='create_match'),
    path('join/<int:match_id>/', views.join_match_view, name='join_match'),
    path('get_match_slots/', views.get_match_slots_ajax, name='get_match_slots_ajax'),
]
