# main/urls.py
from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    path("", views.blog_list_view, name="blog-list"),
    path("create/", views.blog_create_view, name="blog-create"),
    path("<uuid:pk>/update/", views.blog_update_view, name="blog-update"),
    path("<uuid:pk>/delete/", views.blog_delete_view, name="blog-delete"),
    path("<uuid:pk>/", views.blog_detail_view, name="blog-detail"),

    # Endpoint AJAX khusus untuk mengambil form
    path("form/", views.get_blog_form, name="get-blog-form"),
    path("<uuid:pk>/form/", views.get_blog_form, name="get-blog-form"), # Untuk edit
    # JSON API endpoints
    path("json/", views.blog_list_json, name="blog-list-json"),
    path("<uuid:pk>/json/", views.blog_detail_json, name="blog-detail-json"),

    path('create-flutter/', views.create_blog_flutter, name='create_blog_flutter'),
    path('proxy-image/', views.proxy_image, name='proxy_image'),
    path('edit-flutter/<uuid:pk>/', views.edit_blog_flutter, name='edit_blog_flutter'),
    path('delete-flutter/<uuid:pk>/', views.delete_blog_flutter, name='delete_blog_flutter'),
]