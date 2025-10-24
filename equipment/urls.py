from django.urls import path
from . import views

urlpatterns = [
    path('', views.equipment_list, name='equipment_list'),
    path('<int:id>/', views.equipment_detail, name='equipment_detail'),
    path('add/', views.add_equipment, name='add_equipment'),
]
