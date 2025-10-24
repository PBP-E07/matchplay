from django.shortcuts import render

from fields.models import Field

# Create your views here.
def show_main(request):
    fields = Field.objects.all()

    context = { "fields":  fields }

    return render(request, "main.html", context)
