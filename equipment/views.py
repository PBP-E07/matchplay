from django.shortcuts import render, get_object_or_404
from .models import Equipment
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.core import serializers
import json

def is_admin(user):
    if user.is_staff: 
        return True
    raise PermissionDenied 

@login_required
def equipment_list(request):
    equipments = Equipment.objects.all()
    return render(request, 'equipment/list.html', {'equipments': equipments})

def equipment_detail(request, id):
    equipment = get_object_or_404(Equipment, id=id)
    return render(request, 'equipment/detail.html', {'equipment': equipment})

@csrf_exempt
@require_POST
@login_required
@user_passes_test(lambda u: u.is_staff)
def add_equipment(request):
    name = request.POST.get('name')
    quantity = request.POST.get('quantity')
    price_per_hour = request.POST.get('price_per_hour')
    description = request.POST.get('description')
    image = request.FILES.get('image')  

    if not all([name, quantity, price_per_hour, image]):
        return JsonResponse({'error': 'Semua field wajib diisi'}, status=400)

    new_item = Equipment.objects.create(
        name=name,
        quantity=quantity,
        price_per_hour=price_per_hour,
        description=description,
        image=image  
    )

    return JsonResponse({
        'id': new_item.id,
        'name': new_item.name,
        'price_per_hour': str(new_item.price_per_hour),
        'quantity': new_item.quantity,
        'image_url': new_item.image.url
    })
    
@require_POST
@login_required
@user_passes_test(lambda u: u.is_staff)
def edit_equipment(request, id):
    equipment = get_object_or_404(Equipment, id=id)
    equipment.name = request.POST.get('name')
    equipment.quantity = request.POST.get('quantity')
    equipment.price_per_hour = request.POST.get('price_per_hour')
    equipment.description = request.POST.get('description')
    if 'image' in request.FILES:
        equipment.image = request.FILES['image']
    equipment.save()
    return JsonResponse({'status': 'success'})

@require_POST
@login_required
@user_passes_test(lambda u: u.is_staff)
def delete_equipment(request, id):
    equipment = get_object_or_404(Equipment, id=id)
    equipment.delete()
    return JsonResponse({'status': 'deleted'})

@login_required
def equipment_json_detail(request, id):
    equipment = get_object_or_404(Equipment, id=id)
    return JsonResponse({
        'id': equipment.id,
        'name': equipment.name,
        'quantity': equipment.quantity,
        'price_per_hour': str(equipment.price_per_hour),
        'description': equipment.description or ''
    })

def show_json(request):
    data = Equipment.objects.all()
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")

@csrf_exempt
def create_equipment_flutter(request):
    if request.method == 'POST':
        try:
            # 1. Baca data dari JSON body (karena Flutter kirim JSON)
            data = json.loads(request.body)
            
            # 2. Bikin object baru (TANPA field 'user' karena di model gak ada)
            new_equipment = Equipment.objects.create(
                name=data["name"],
                quantity=int(data["quantity"]),
                price_per_hour=float(data["price_per_hour"]),
                description=data["description"],
                # Image kita skip dulu (biarkan null) biar gak ribet error upload
            )
            
            new_equipment.save()

            return JsonResponse({"status": "success"}, status=200)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
            
    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=401)

@csrf_exempt
@require_POST
def edit_equipment_flutter(request, id):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "Login required"}, status=401)
    
    if not request.user.is_staff: # Hanya admin yang boleh edit
        return JsonResponse({"status": "error", "message": "Permission denied"}, status=403)

    try:
        equipment = get_object_or_404(Equipment, pk=id)
        data = json.loads(request.body)

        equipment.name = data['name']
        equipment.quantity = int(data['quantity'])
        equipment.price_per_hour = float(data['price_per_hour'])
        equipment.description = data['description']
        equipment.save()

        return JsonResponse({"status": "success", "message": "Equipment updated!"}, status=200)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@csrf_exempt
@require_POST
def delete_equipment_flutter(request, id):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "Login required"}, status=401)
    
    if not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "Permission denied"}, status=403)

    try:
        equipment = get_object_or_404(Equipment, pk=id)
        equipment.delete()
        return JsonResponse({"status": "success", "message": "Equipment deleted!"}, status=200)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)