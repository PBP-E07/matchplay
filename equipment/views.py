from django.shortcuts import render, get_object_or_404
from .models import Equipment

def equipment_list(request):
    equipments = Equipment.objects.all()
    return render(request, 'equipment/list.html', {'equipments': equipments})

def equipment_detail(request, id):
    equipment = get_object_or_404(Equipment, id=id)
    return render(request, 'equipment/detail.html', {'equipment': equipment})
