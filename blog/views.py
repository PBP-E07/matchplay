# main/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from .models import Blog
from .forms import BlogForm
import json
from django.urls import reverse

# Halaman Utama (Seperti di Gambar)
def blog_list_view(request):
    blogs = Blog.objects.all()
    blog_count = blogs.count()
    return render(request, 'main/blog_list.html', {
        'blogs': blogs,
        'blog_count': blog_count
    })

# View untuk "Read More" (Biasa)
def blog_detail_view(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    # Opsional: hitung views
    blog.increment_views() 
    return render(request, 'main/blog_detail.html', {'blog': blog})


# --- AJAX Views ---

# 1. View untuk MENGAMBIL form (Create / Edit)
def get_blog_form(request, pk=None):
    if pk:
        # Ini untuk Edit
        blog = get_object_or_404(Blog, pk=pk)
        form = BlogForm(instance=blog)
        # URL untuk form action akan ke 'blog-update'
        form_url = reverse('main:blog-update', kwargs={'pk': pk})
        form_title = "Edit Blog"
    else:
        # Ini untuk Create
        form = BlogForm()
        # URL untuk form action akan ke 'blog-create'
        form_url = reverse('main:blog-create')
        form_title = "Create New Blog"
        
    context = {
        'form': form,
        'form_url': form_url,
        'form_title': form_title,
    }
    # Render form ke string HTML
    html_form = render_to_string('main/_blog_form.html', context, request=request)
    return JsonResponse({'html_form': html_form})

# 2. View untuk CREATE Blog (Handle POST dari AJAX)
def blog_create_view(request):
    if request.method == 'POST':
        form = BlogForm(request.POST)
        if form.is_valid():
            blog = form.save()
            # Render card baru ke string HTML
            new_card_html = render_to_string('main/_blog_card.html', {'blog': blog})
            return JsonResponse({
                'success': True, 
                'new_card_html': new_card_html
            })
        else:
            # Kirim error form jika tidak valid
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

# 3. View untuk UPDATE Blog (Handle POST dari AJAX)
def blog_update_view(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    if request.method == 'POST':
        form = BlogForm(request.POST, instance=blog)
        if form.is_valid():
            blog = form.save()
            # Render card yang diupdate ke string HTML
            updated_card_html = render_to_string('main/_blog_card.html', {'blog': blog})
            return JsonResponse({
                'success': True,
                'updated_card_html': updated_card_html,
                'pk': pk
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

# 4. View untuk DELETE Blog (Handle DELETE dari AJAX)
def blog_delete_view(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    if request.method == 'POST': # HTML forms tidak support 'DELETE' method, jadi kita pakai POST
        blog.delete()
        return JsonResponse({'success': True, 'pk': pk})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})