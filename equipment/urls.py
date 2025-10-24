from django.urls import path
from . import views

app_name = "equipment"

urlpatterns = [
    path('', views.equipment_list, name='equipment_list'),
    path('<int:id>/', views.equipment_detail, name='equipment_detail'),
]
