from django.urls import path
from . import views

app_name = "equipment"

urlpatterns = [
    path('', views.equipment_list, name='equipment_list'),
    path('add/', views.add_equipment, name='add_equipment'),
    path('<int:id>/detail/', views.equipment_json_detail, name='equipment_detail_json'),
    path('<int:id>/edit/', views.edit_equipment, name='edit_equipment'),
    path('<int:id>/delete/', views.delete_equipment, name='delete_equipment'),
]

