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
from datetime import datetime
from django.db.models import Sum
from .models import Equipment, Rental
from django.utils.timezone import make_aware
from django.utils import timezone

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

def check_availability(request, id):
    date_str = request.GET.get('date')
    if not date_str:
        return JsonResponse({'availability': []})

    eq = get_object_or_404(Equipment, id=id)
    
    try:
        # 1. Pastikan parsing tanggal benar
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({'error': 'Format tanggal salah. Gunakan YYYY-MM-DD'}, status=400)

    availability_data = []
    # 2. Loop jam 06.00 sampai 00.00 (24)
    for i in range(6, 24):
        start_h = f"{i:02d}.00"
        end_h = f"{(i+1):02d}.00" if i < 23 else "00.00"
        slot = f"{start_h}-{end_h}"
        
        # 3. Buat waktu jadi TIMEZONE AWARE biar gak crash
        s_time = make_aware(datetime.strptime(f"{date_str} {start_h}", "%Y-%m-%d %H.%M"))
        # Jika jam 00.00, berarti itu hari berikutnya
        if i == 23:
            e_time = s_time + timezone.timedelta(hours=1)
        else:
            e_time = make_aware(datetime.strptime(f"{date_str} {end_h}", "%Y-%m-%d %H.%M"))

        # 4. Hitung stok yang sudah dipesan
        rented_count = Rental.objects.filter(
            equipment=eq,
            start_time__lt=e_time,
            end_time__gt=s_time
        ).aggregate(total=Sum('quantity_rented'))['total'] or 0
        
        remaining_stock = eq.quantity - rented_count

        availability_data.append({
            'slot': slot,
            'stock': max(0, remaining_stock)
        })

    return JsonResponse({'availability': availability_data})

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
    # Cek apakah image itu URL atau file path
    image_url = str(equipment.image)
    if not image_url.startswith('http'):
        image_url = request.build_absolute_uri(equipment.image.url) if equipment.image else ''

    return JsonResponse({
        'id': equipment.id,
        'name': equipment.name,
        'quantity': equipment.quantity,
        'price_per_hour': str(equipment.price_per_hour),
        'description': equipment.description or '',
        'image_url': image_url  # Ini yang akan dipake Image.network di Flutter
    })

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
def book_equipment(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'error', 'message': 'Sesi habis, login lagi bro!'}, status=403)

        try:
            data = json.loads(request.body)
            eq = get_object_or_404(Equipment, id=data['eq_id'])
            date_str = data['date'] 
            slot = data['slot']     
            requested_qty = int(data.get('quantity', 1))
            
            # --- FIX DISINI ---
            # 1. Hapus spasi dan ganti titik (.) jadi titik dua (:) supaya konsisten
            clean_slot = slot.replace(" ", "").replace(".", ":") 
            
            # 2. Split jam awal dan akhir
            start_h, end_h = clean_slot.split('-')
            
            # 3. Parse waktu (sekarang aman pakai %H:%M karena sudah di-replace tadi)
            start_time = make_aware(datetime.strptime(f"{date_str} {start_h}", "%Y-%m-%d %H:%M"))
            
            # Handle jam 00:00 atau 24:00 agar tidak error (pindah ke hari berikutnya)
            if end_h in ["00:00", "24:00", "00.00"]:
                end_time = start_time + timezone.timedelta(hours=1)
            else:
                end_time = make_aware(datetime.strptime(f"{date_str} {end_h}", "%Y-%m-%d %H:%M"))

            # --- LOGIKA STOK ---
            rented_sum = Rental.objects.filter(
                equipment=eq,
                start_time__lt=end_time,
                end_time__gt=start_time
            ).aggregate(total=Sum('quantity_rented'))['total'] or 0

            if rented_sum + requested_qty > eq.quantity:
                return JsonResponse({
                    'status': 'error', 
                    'message': f'Stok sisa {eq.quantity - rented_sum}'
                }, status=400)

            # SIMPAN
            Rental.objects.create(
                equipment=eq,
                renter_name=request.user.username,
                quantity_rented=requested_qty,
                start_time=start_time,
                end_time=end_time
            )
            
            return JsonResponse({'status': 'success'}, status=200)

        except Exception as e:
            # SANGAT PENTING: Print error di terminal biar lo tau error aslinya apa
            print(f"DEBUG ERROR BOOKING: {e}") 
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    
def show_json(request):
    data = Equipment.objects.all()
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")

@login_required
def my_bookings(request):
    # Mengambil data sewa user yang login, urutkan dari yang terbaru
    bookings = Rental.objects.filter(renter_name=request.user.username).order_by('-start_time')
    return render(request, 'equipment/my_bookings.html', {'bookings': bookings})

@csrf_exempt
def edit_equipment_flutter(request, id):
    if request.method != 'POST':
        return JsonResponse({"status": "error"}, status=400)

    try:
        data = json.loads(request.body)
        equipment = Equipment.objects.get(pk=id)

        if "name" in data:
            equipment.name = data["name"]

        if "price" in data:
            equipment.price_per_hour = float(data["price"])

        if "stock" in data:
            equipment.quantity = int(data["stock"])

        if "description" in data:
            equipment.description = data["description"]

        if "image" in data:
            equipment.image = data["image"]

        equipment.save()
        return JsonResponse({"status": "success"}, status=200)

    except Equipment.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Alat tidak ditemukan"}, status=404)

    except Exception as e:
        print("EDIT EQUIPMENT ERROR:", e)
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@csrf_exempt
def delete_equipment_flutter(request, id):
    if request.method == 'POST':
        equipment = Equipment.objects.get(pk=id)
        equipment.delete()
        return JsonResponse({"status": "success"}, status=200)
    return JsonResponse({"status": "error"}, status=400)