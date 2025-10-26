from django.urls import path
from dashboard import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('filter-panel/', views.filter_panel, name='filter_panel'),
    path('add_ajax/', views.add_field_ajax, name='add_field_ajax'),
    path('edit_ajax/<int:pk>/', views.edit_field_ajax, name='edit_field_ajax'),
    path('delete_ajax/<int:pk>/', views.delete_field_ajax, name='delete_field_ajax')
]
