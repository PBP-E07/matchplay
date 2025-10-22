from django.shortcuts import render
from django.core.paginator import Paginator
from fields.models import Field
from django.http import JsonResponse
from django.template.loader import render_to_string

def dashboard_home(request):
    field_list = Field.objects.all().order_by('name')

    total_fields = field_list.count()
    avg_price = round(sum(f.price for f in field_list) / total_fields, 2) if total_fields > 0 else 0
    avg_rating = round(sum(float(f.rating) for f in field_list) / total_fields, 2) if total_fields > 0 else 0

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
    page_number = request.GET.get('page')
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
            'page_info_html': page_info_html
        })
    
    return render(request, 'dashboard/home.html', context)

def filter_panel(request):
    html = render_to_string('dashboard/filter_panel.html', {
        'sport_categories': Field.SPORT_CATEGORY,
    })
    return JsonResponse({'html': html})