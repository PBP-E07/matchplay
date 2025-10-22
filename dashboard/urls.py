from django.urls import path
from dashboard import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('filter-panel/', views.filter_panel, name='filter_panel'),
    path('add_ajax/', views.add_field_ajax, name='add_field_ajax')
]
