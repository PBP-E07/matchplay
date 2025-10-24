from django.shortcuts import render
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.http import HttpResponse
from fields.models import Field
from django.db.models import Q

def show_main(request):
    query = request.GET.get('q', '')
    
    if query:
        field_list = Field.objects.filter(
            Q(name__icontains=query) | 
            Q(location__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()
    else:
        field_list = Field.objects.all().order_by('name')

    paginator = Paginator(field_list, 9) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'fields': page_obj, 
    }
    return render(request, 'main.html', context)

def search_fields(request):
    query = request.GET.get('q', '')
    
    if query:
        field_list = Field.objects.filter(
            Q(name__icontains=query) | 
            Q(location__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()
    else:
        field_list = Field.objects.all().order_by('name')

    paginator = Paginator(field_list, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'request': request,
    }
    
    html = render_to_string('partials/field_list_content.html', context)
    
    return HttpResponse(html)
