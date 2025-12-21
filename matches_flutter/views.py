from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from fields.models import Field
from matches_flutter.models import Match

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
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
            match = Match.objects.create(
                field=field,
                creator=request.user,
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
        