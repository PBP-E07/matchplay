from django.urls import path
from django.urls import path
from .views import equipment_list, add_equipment, equipment_json_detail, edit_equipment, delete_equipment, show_json, create_equipment_flutter, edit_equipment_flutter, delete_equipment_flutter
from . import views
from .views import show_json

app_name = "equipment"

urlpatterns = [
    path('', views.equipment_list, name='equipment_list'),
    path('add/', views.add_equipment, name='add_equipment'),
    path('<int:id>/detail/', views.equipment_json_detail, name='equipment_detail_json'),
    path('<int:id>/edit/', views.edit_equipment, name='edit_equipment'),
    path('<int:id>/delete/', views.delete_equipment, name='delete_equipment'),
    path('json/', show_json, name='show_json'),
    path('create-flutter/', create_equipment_flutter, name='create_equipment_flutter'),
    path('book/', views.book_equipment, name='book_equipment'),
    path('<int:id>/availability/', views.check_availability, name='check_availability'),
    path('edit-flutter/<int:id>/', edit_equipment_flutter, name='edit_equipment_flutter'),
    path('delete-flutter/<int:id>/', delete_equipment_flutter, name='delete_equipment_flutter'),
]

