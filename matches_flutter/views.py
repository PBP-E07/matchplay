from django.views.decorators.csrf import csrf_exempt  #
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from fields.models import Field
from matches_flutter.models import Match

@csrf_exempt
@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def match_list_api(request):
    if request.method == "GET":
        matches = Match.objects.select_related("field").all().order_by("date", "time_slot")
        data = []
        for match in matches:
            data.append({
                "id": match.id,
                "field_name": match.field.name, 
                "time_slot": match.time_slot,
                "date": str(match.date),
                "price": match.price,
                "current_players": match.current_players,
                "max_players": match.max_players,
                "progress": match.progress,
            })
        return Response({"status": "success", "data": data})

    elif request.method == "POST":
        data = request.data
        
        field_id = data.get("field_id")
        time_slot = data.get("time_slot")
        date_str = data.get("date")
        
        if Match.objects.filter(field_id=field_id, date=date_str, time_slot=time_slot).exists():
            return Response(
                {"status": "error", "message": "This time slot is already booked for this field."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            field = Field.objects.get(id=field_id)
            
            creator_user = request.user
            if not creator_user.is_authenticated:
                creator_user = User.objects.first()
                if not creator_user:
                    return Response({"status": "error", "message": "No users found in database to assign match to."}, status=500)

            match = Match.objects.create(
                field=field,
                creator=creator_user,
                date=date_str,
                time_slot=time_slot,
                price=data.get("price", 50000),
                max_players=data.get("max_players", 10)
            )
            
            response_data = {
                "id": match.id,
                "field_name": match.field.name,
                "time_slot": match.time_slot,
                "date": str(match.date),
                "price": match.price,
                "current_players": match.current_players,
                "max_players": match.max_players,
            }
            
            return Response(
                {"status": "success", "message": "Match created successfully!", "data": response_data},
                status=status.HTTP_201_CREATED
            )
        except Field.DoesNotExist:
            return Response({"status": "error", "message": "Field not found"}, status=404)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=500)

@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def get_occupied_slots(request):
    field_id = request.GET.get('field_id')
    date_str = request.GET.get('date')

    if not field_id or not date_str:
        return Response(
            {"status": "error", "message": "field_id and date are required"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    occupied_slots = Match.objects.filter(
        field_id=field_id, 
        date=date_str
    ).values_list('time_slot', flat=True)

    return Response({
        "status": "success", 
        "occupied_slots": list(occupied_slots)
    })
