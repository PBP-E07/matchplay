import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.models import User
from fields.models import Field
from matches_flutter.models import Match

@csrf_exempt
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
        return JsonResponse({"status": "success", "data": data}, status=200)

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = request.POST

        field_id = data.get("field_id")
        time_slot = data.get("time_slot")
        date_str = data.get("date")
        
        if Match.objects.filter(field_id=field_id, date=date_str, time_slot=time_slot).exists():
            return JsonResponse(
                {"status": "error", "message": "This time slot is already booked."},
                status=400
            )

        try:
            field = Field.objects.get(id=field_id)
        except Field.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Field not found"}, status=404)

        creator_user = request.user
        if not creator_user.is_authenticated:
            creator_user = User.objects.first()
            if not creator_user:
                return JsonResponse({"status": "error", "message": "No users in DB"}, status=500)

        try:
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
            }
            
            return JsonResponse(
                {"status": "success", "message": "Match created!", "data": response_data},
                status=201
            )
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    else:
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

@csrf_exempt
def get_occupied_slots(request):
    if request.method == "GET":
        field_id = request.GET.get('field_id')
        date_str = request.GET.get('date')

        if not field_id or not date_str:
            return JsonResponse(
                {"status": "error", "message": "field_id and date are required"}, 
                status=400
            )

        occupied_slots = Match.objects.filter(
            field_id=field_id, 
            date=date_str
        ).values_list('time_slot', flat=True)

        return JsonResponse({
            "status": "success", 
            "occupied_slots": list(occupied_slots)
        }, status=200)
    
    else:
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)
    
@csrf_exempt
def join_match_api(request, match_id):
    if request.method == "POST":
        try:
            match = Match.objects.get(id=match_id)
            
            if match.current_players >= match.max_players:
                return JsonResponse(
                    {"status": "error", "message": "Match is full!"}, 
                    status=400
                )

            match.current_players += 1
            match.save()
            
            return JsonResponse(
                {"status": "success", "message": "Successfully joined the match!"}, 
                status=200
            )
            
        except Match.DoesNotExist:
            return JsonResponse(
                {"status": "error", "message": "Match not found"}, 
                status=404
            )
            
    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)
