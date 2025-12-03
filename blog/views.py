# main/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from .models import Blog
from .forms import BlogForm
import json
from django.urls import reverse
from authentication.decorators import admin_required
from django.utils.html import strip_tags
from django.views.decorators.csrf import csrf_exempt
import requests

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


# --- JSON API Views ---
def blog_list_json(request):
    """Return a JSON list of blogs."""
    blogs = Blog.objects.all()
    data = []
    for b in blogs:
        data.append({
            'id': str(b.id),
            'title': b.title,
            'summary': b.summary,
            'content': b.content,
            'thumbnail': b.thumbnail,
            'author': b.author,
            'created_at': b.created_at.isoformat() if b.created_at else None,
            'blog_views': b.blog_views,
            'url': b.get_absolute_url(),
        })
    return JsonResponse({'blogs': data})


def blog_detail_json(request, pk):
    """Return a JSON object for a single blog (by UUID pk)."""
    blog = get_object_or_404(Blog, pk=pk)
    # Keep same behavior as HTML detail: increment views
    blog.increment_views()
    data = {
        'id': str(blog.id),
        'title': blog.title,
        'summary': blog.summary,
        'content': blog.content,
        'thumbnail': blog.thumbnail,
        'author': blog.author,
        'created_at': blog.created_at.isoformat() if blog.created_at else None,
        'blog_views': blog.blog_views,
        'url': blog.get_absolute_url(),
    }
    return JsonResponse({'blog': data})


# --- AJAX Views ---

# 1. View untuk MENGAMBIL form (Create / Edit)
@admin_required
def get_blog_form(request, pk=None):
    if pk:
        # Ini untuk Edit
        blog = get_object_or_404(Blog, pk=pk)
        form = BlogForm(instance=blog)
        # URL untuk form action akan ke 'blog-update'
        form_url = reverse('blog:blog-update', kwargs={'pk': pk})
        form_title = "Edit Blog"
    else:
        # Ini untuk Create
        form = BlogForm()
        # URL untuk form action akan ke 'blog-create'
        form_url = reverse('blog:blog-create')
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
@admin_required
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
@admin_required
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
@admin_required
def blog_delete_view(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    if request.method == 'POST': # HTML forms tidak support 'DELETE' method, jadi kita pakai POST
        blog.delete()
        return JsonResponse({'success': True, 'pk': pk})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

# --- Mobile ---
@csrf_exempt
def create_blog_flutter(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        title = strip_tags(data.get("title", ""))  # Strip HTML tags
        summary = strip_tags(data.get("summary", ""))  # Strip HTML tags
        content = strip_tags(data.get("content", ""))  # Strip HTML tags
        thumbnail = data.get("thumbnail", "")
        author = strip_tags(data.get("author", ""))  # Strip HTML tags
        
        new_blog = Blog(
            title=title,
            summary=summary,
            content=content,
            thumbnail=thumbnail,
            author=author,
        )
        new_blog.save()
        
        return JsonResponse({"status": "success"}, status=200)
    else:
        return JsonResponse({"status": "error"}, status=401)
    
def proxy_image(request):
    image_url = request.GET.get('url')
    if not image_url:
        return HttpResponse('No URL provided', status=400)
    
    try:
        # Fetch image from external source
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        # Return the image with proper content type
        return HttpResponse(
            response.content,
            content_type=response.headers.get('Content-Type', 'image/jpeg')
        )
    except requests.RequestException as e:
        return HttpResponse(f'Error fetching image: {str(e)}', status=500)
    
@csrf_exempt
def edit_blog_flutter(request, pk):
    if request.method == 'POST':
        blog = get_object_or_404(Blog, pk=pk)
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

        blog.title = strip_tags(data.get("title", blog.title))
        blog.summary = strip_tags(data.get("summary", blog.summary))
        blog.content = strip_tags(data.get("content", blog.content))
        blog.thumbnail = data.get("thumbnail", blog.thumbnail)
        blog.author = strip_tags(data.get("author", blog.author))
        blog.save()

        return JsonResponse({"status": "success"}, status=200)
    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

@csrf_exempt
def delete_blog_flutter(request, pk):
    if request.method == 'POST':
        blog = get_object_or_404(Blog, pk=pk)
        blog.delete()
        return JsonResponse({"status": "success"}, status=200)
    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)