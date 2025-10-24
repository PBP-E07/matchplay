from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from fields.models import Field
from fields.forms import FieldForm

def dashboard_home(request):
    field_list = Field.objects.all().order_by('name')

    total_fields = field_list.count()
    avg_price = round(sum(f.price for f in field_list) / total_fields, 2) if total_fields > 0 else 0
    avg_rating = round(sum(f.rating for f in field_list) / total_fields, 2) if total_fields > 0 else 0

    # ===== FILTERING =====
    # === CATEGORY ===
    # Parameter dari GET request: jenis kategori
    selected_category = request.GET.get('category', '')

    # Filter berdasarkan kategori (jika dipilih)
    if selected_category:
        field_list = field_list.filter(sport=selected_category)

    # === PRICE ===
    # Parameter dari GET request: min dan max price
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    # Filter berdasarkan harga
    if min_price:
        field_list = field_list.filter(price__gte=min_price)
    if max_price:
        field_list = field_list.filter(price__lte=max_price)

    # ===== PAGING =====
    # Parameter dari GET request: jumlah row per page
    per_page = int(request.GET.get('per_page', 20))

    # Melakukan paging
    paginator = Paginator(field_list, per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'total_fields': total_fields,
        'avg_price': avg_price,
        'avg_rating': avg_rating,
        'per_page_choices': [5, 10, 20, 50, 100],
        'current_per_page': per_page,
        'sport_categories': [category[0] for category in Field.SPORT_CATEGORY],
        'selected_category': selected_category,
        'min_price': min_price,
        'max_price': max_price
    }

    # Jika request AJAX, kembalikan partial HTML tabel
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        table_html = render_to_string('dashboard/field_table.html', context, request=request)
        pagination_html = render_to_string('dashboard/pagination.html', context, request=request)
        page_info_html = render_to_string('dashboard/page_info.html', context, request=request)
        return JsonResponse({
            'table_html': table_html,
            'pagination_html': pagination_html,
            'page_info_html': page_info_html,
            'total_fields': total_fields,
            'avg_price': avg_price,
            'avg_rating': round(avg_rating, 2)
        })
    
    return render(request, 'dashboard/home.html', context)

def add_field_ajax(request):
    if request.method == 'POST':
        form = FieldForm(request.POST)
        if form.is_valid():
            form.save()
            # Render partial tabel terbaru
            field_list = Field.objects.all().order_by('name')[:20]  # sesuaikan per_page
            table_html = render_to_string('dashboard/field_table.html', {'page_obj': field_list}, request=request)
            return JsonResponse({'success': True, 'table_html': table_html})
        else:
            # Kembalikan form beserta error
            form_html = render_to_string('dashboard/add_field_form.html', {'form': form}, request=request)
            return JsonResponse({'success': False, 'form_html': form_html})
    else:
        form = FieldForm()
        form_html = render_to_string('dashboard/add_field_form.html', {'form': form}, request=request)
        return JsonResponse({'form_html': form_html})

def edit_field_ajax(request, pk):
    field_obj = Field.objects.get(pk=pk)
    if request.method == 'POST':
        form = FieldForm(request.POST, instance=field_obj)
        if form.is_valid():
            form.save()
            field_list = Field.objects.all().order_by('name')
            table_html = render_to_string('dashboard/field_table.html', {'field_list': field_list}, request=request)
            return JsonResponse({'success': True, 'table_html': table_html})
        else:
            form_html = render_to_string('dashboard/add_field_form.html', {'form': form}, request=request)
            return JsonResponse({'success': False, 'form_html': form_html})
    else:
        form = FieldForm(instance=field_obj)
        form_html = render_to_string('dashboard/add_field_form.html', {'form': form}, request=request)
        return JsonResponse({'form_html': form_html})

@csrf_exempt
def delete_field_ajax(request, pk):
    if request.method == 'POST':
        field_obj = Field.objects.get(pk=pk)
        field_obj.delete()
        field_list = Field.objects.all().order_by('name')
        table_html = render_to_string('dashboard/field_table.html', {'field_list': field_list}, request=request)
        return JsonResponse({'success': True, 'table_html': table_html})

def filter_panel(request):
    html = render_to_string('dashboard/filter_panel.html', {
        'sport_categories': Field.SPORT_CATEGORY,
    })
    return JsonResponse({'html': html})