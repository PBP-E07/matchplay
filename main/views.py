from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpResponse
from fields.models import Field
from django.db.models import Q

def show_main(request):
    query = request.GET.get("q", "")
    
    if query:
        field_list = Field.objects.filter(
            Q(name__icontains=query) | 
            Q(location__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()
    else:
        field_list = Field.objects.all().order_by("name")

    context = {
        "fields": field_list
    }

    return render(request, "main.html", context)

def search_fields(request):
    query = request.GET.get("q", "")
    
    if query:
        field_list = Field.objects.filter(
            Q(name__icontains=query) | 
            Q(location__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()
    else:
        field_list = Field.objects.all().order_by("name")

    context = {
        "field_list": field_list,
        "request": request,
    }
    
    html = render_to_string("partials/field_list_content.html", context)
    
    return HttpResponse(html)
