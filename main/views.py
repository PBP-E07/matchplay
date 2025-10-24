from django.shortcuts import render
from django.db.models import Q
from fields.models import Field

def show_main(request):
    fields = Field.objects.all()

    return render(request, "main.html", { "fields": fields })

def search_fields(request):
    query = request.GET.get("q", "")

    fields = Field.objects.filter(
        Q(name__icontains=query) |
        Q(location__icontains=query) |
        Q(sport__icontains=query)
    )

    return render(request, "partials/field_list.html", { "fields": fields })
