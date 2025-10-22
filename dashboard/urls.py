from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('filter-panel/', views.filter_panel, name='filter_panel')
]
