# main/urls.py
from django.urls import path
from . import views

app_name = "blog" # Penting untuk namespacing

urlpatterns = [
    path("blog/", views.blog_list_view, name="blog-list"),
    path("blog/create/", views.blog_create_view, name="blog-create"),
    path("blog/<uuid:pk>/update/", views.blog_update_view, name="blog-update"),
    path("blog/<uuid:pk>/delete/", views.blog_delete_view, name="blog-delete"),
    path("blog/<uuid:pk>/", views.blog_detail_view, name="blog-detail"),

    # Endpoint AJAX khusus untuk mengambil form
    path("blog/form/", views.get_blog_form, name="get-blog-form"),
    path("blog/<uuid:pk>/form/", views.get_blog_form, name="get-blog-form"), # Untuk edit
]