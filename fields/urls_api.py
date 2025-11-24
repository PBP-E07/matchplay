from django.urls import path
from fields import views_api

app_name = 'api_fields'

urlpatterns = [
    path('', views_api.field_list_api, name='list'),
    path('<int:pk>/', views_api.field_detail_api, name='detail'),
]