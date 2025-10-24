# bookings/urls.py
from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('book/<int:field_id>/', views.book_field, name='book_field'),
    path('get_slots/<int:field_id>/', views.get_available_slots_ajax, name='get_available_slots_ajax'),
]