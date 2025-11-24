from django.db.models import Q, Avg
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from fields.models import Field
from fields.serializers import FieldSerializer

# ===== HELPER METHOD =====

# Filtering dan Searching
def apply_field_filters(queryset, params):
    """
    Menangani semua logika filtering (Search, Category, Price).
    params: request.GET
    """
    # Search (nama & lokasi)
    search_query = params.get('search', '')
    if search_query:
        queryset = queryset.filter(
            Q(name__icontains=search_query) | 
            Q(location__icontains=search_query)
        )

    # Filter category
    selected_category = params.get('category')
    if selected_category:
        queryset = queryset.filter(sport__iexact=selected_category)

    # Filter price (dengan error handling)
    try:
        if min_price := params.get('min_price'):
            queryset = queryset.filter(price__gte=int(min_price))
        if max_price := params.get('max_price'):
            queryset = queryset.filter(price__lte=int(max_price))

    # Abaikan jika input bukan harga
    except ValueError:
        pass

    return queryset

# Pagination dan Meta Data
def get_pagination_data(queryset, page_number, per_page):
    """
    Menangani Paginator dan menghitung rata-rata (Aggregation).
    Mengembalikan tuple: (page_obj, meta_dict)
    """
    # Aggregation (Hitung rata-rata)
    total_fields = queryset.count()
    aggregates = queryset.aggregate(avg_price=Avg('price'), avg_rating=Avg('rating'))
    
    # Setup paginator
    paginator = Paginator(queryset, per_page)
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Susun metadata untuk Flutter
    meta_data = {
        "total_data": total_fields,
        "total_pages": paginator.num_pages,
        "current_page": page_obj.number,
        "avg_price": round(aggregates['avg_price'] or 0, 2),
        "avg_rating": round(aggregates['avg_rating'] or 0, 2)
    }

    return page_obj, meta_data

# Validasi Input dan Save
def handle_validation_and_save(serializer, success_status=status.HTTP_200_OK):
    """
    Method reusable untuk memvalidasi dan menyimpan data dari serializer.
    Mencegah penulisan ulang logika if-else is_valid() di setiap view.
    """
    # Melakukan validasi dan save jika berhasil
    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": "success",
            "message": "Data berhasil disimpan!",
            "data": serializer.data
        }, status=success_status)
    
    # Jika gagal validasi
    return Response({
        "status": "error",
        "message": "Data tidak valid!",
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

# ===== VIEWS METHOD =====

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def field_list_api(request):
    """
    GET: Tampilkan semua fields (JSON)
    POST: Buat field baru (JSON)
    """
    # GET boleh diakses user biasa (Sudah login)
    if request.method == 'GET':
        # 1. Base query
        queryset = Field.objects.all().order_by('name')

        # 2. Melakukan filtering
        queryset = apply_field_filters(queryset, request.GET)

        # 3. Melakukan paginasi dan mendapatkan metadata
        per_page = int(request.GET.get('per_page', 20))
        page_number = request.GET.get('page', 1)
        page_obj, meta_data = get_pagination_data(queryset, page_number, per_page)

        # 4. Serialize dan return Response
        serializer = FieldSerializer(page_obj.object_list, many=True)
        return Response({
            "status": "success",
            "data": {
                "fields": serializer.data,
                "meta": meta_data
            }
        })

    # POST hanya boleh diakses oleh admin (is_staff)
    elif request.method == 'POST':
        if not request.user.is_staff:
             return Response(
                {"status": "error", "message": "Hanya admin yang boleh menambahkan data!"},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = FieldSerializer(data=request.data)
        return handle_validation_and_save(serializer, success_status=status.HTTP_201_CREATED)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def field_detail_api(request, pk):
    """
    GET: Ambil satu field detail
    PATCH: Update field
    DELETE: Hapus field
    """
    field = get_object_or_404(Field, pk=pk)

    # GET boleh diakses oleh user biasa (Sudah login)
    if request.method == 'GET':
        serializer = FieldSerializer(field)
        return Response(serializer.data)

    # Cek apakah user adalah admin (is_staff) sebelum lanjut ke PATCH atau DELETE
    if not request.user.is_staff:
        return Response(
            {"status": "error", "message": "Hanya admin yang boleh mengubah/menghapus data."},
            status=status.HTTP_403_FORBIDDEN
        )

    # PATCH hanya boleh diakses oleh admin (is_staff)
    if request.method == 'PATCH':
        serializer = FieldSerializer(field, data=request.data, partial=True)
        return handle_validation_and_save(serializer)

    # DELETE hanya boleh diakses oleh admin (is_staff)
    elif request.method == 'DELETE':
        field.delete()
        return Response({
            "status": "success", 
            "message": "Data berhasil dihapus"
        }, status=status.HTTP_204_NO_CONTENT)