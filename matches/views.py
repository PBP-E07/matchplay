from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from .models import Match, MatchPlayer
from .forms import CreateMatchForm
from django.db import IntegrityError
import datetime
from fields.models import Field 
from bookings.models import Booking

@login_required
def show_matches(request):
    # get date now
    now = timezone.now()

    # get available matches to join
    available_matches_qs = Match.objects.filter(
        status="Pending",
        match_date__gte=now.date()
    ).exclude(
        # exclude those with today's date and less than current time
        match_date=now.date(), end_time__lte=now.time()
    ).select_related("organizer", "field").prefetch_related("matchplayer_set")

    matches_to_display = []
    # get matches to display
    for match in available_matches_qs:
        current_player_count = match.matchplayer_set.count()
        is_full = current_player_count >= match.max_players

        if not is_full:
            match.current_player_count = current_player_count
            match.spots_left = max(0, match.max_players - current_player_count)
            match.is_full = is_full
            
            if match.max_players > 0:
                match.progress_percentage = (current_player_count / match.max_players) * 100
            else:
                match.progress_percentage = 0
            
            matches_to_display.append(match)

    # pass it to context
    context = {
        "matches": matches_to_display,
        "match_count": len(matches_to_display)
    }

    return render(request, "match_list.html", context)

@login_required
def show_create_match(request):
    if request.method == "POST":
        form = CreateMatchForm(request.POST)

        if form.is_valid():
            field = form.cleaned_data["field"]
            match_date = form.cleaned_data["match_date"]
            time_slot_str = form.cleaned_data["time_slot"]
            
            start_time_str, end_time_str = time_slot_str.split("-")
            start_time = datetime.datetime.strptime(start_time_str, "%H:%M").time()
            end_time = datetime.datetime.strptime(end_time_str, "%H:%M").time()

            now = timezone.localtime(timezone.now())

            # similar filtering method to "bookings" app
            if match_date < now.date() or (match_date == now.date() and start_time < now.time()):
                messages.error(request, "Cannot create a match for a time slot that has already passed.")
            
            elif Booking.objects.filter(field=field, booking_date=match_date, start_time=start_time).exists():
                messages.error(request, "This time slot is already booked directly. Please select another.")

            elif Match.objects.filter(field=field, match_date=match_date, start_time=start_time, status__in=["Pending", "Confirmed"]).exists():
                messages.error(request, "This time slot is already taken by another match. Please select another.")
            
            # create match if there is no errors
            else:
                match = Match.objects.create(
                    organizer=request.user,
                    field=field,
                    match_date=match_date,
                    start_time=start_time,
                    end_time=end_time,
                    skill_level=form.cleaned_data["skill_level"],
                    max_players=form.cleaned_data["max_players"],
                    price_per_person=form.cleaned_data["price_per_person"],
                    description=form.cleaned_data["description"],
                    status="Pending"
                )
                
                MatchPlayer.objects.create(match=match, user=request.user)

                messages.success(request, f"Match room created successfully for {match.field.name} on {match.match_date}.")
                return redirect("matches:show_matches")
        
        else:
            messages.error(request, "Please correct the errors in the form below.")
        
        context = { "form": form }
        return render(request, "create_match_form.html", context)

    else:
        form = CreateMatchForm()
        context = { "form": form }
        return render(request, "create_match_form.html", context)

@login_required
@require_POST
def show_join_match(request, match_id):
    match = get_object_or_404(Match.objects.prefetch_related("matchplayer_set"), pk=match_id)

    now = timezone.now()
    match_end_datetime = timezone.make_aware(
        datetime.datetime.combine(match.match_date, match.end_time)
    )
    is_past = match_end_datetime < now
    current_player_count = match.matchplayer_set.count()
    is_full = current_player_count >= match.max_players

    # cannot join completed matches
    if match.status != "Pending":
        messages.error(request, "This match is no longer available to join.")
        return redirect("matches:show_matches")
    if is_past:
        messages.error(request, "This match has already passed.")
        return redirect("matches:show_matches")
    if is_full:
        messages.error(request, "This match is already full.")
        return redirect("matches:show_matches")

    try:
        # try to create a MatchPlayer object
        MatchPlayer.objects.create(match=match, user=request.user)
        messages.success(request, f"Successfully joined the match at {match.field.name}.")
        
        if (current_player_count + 1) >= match.max_players:
            messages.info(request, "The match is now full!")
    except IntegrityError:
        messages.warning(request, "You have already joined this match.")
    except Exception as e:
        messages.error(request, f"An error occurred while joining: {e}")

    return redirect("matches:show_matches")

def get_match_slots_ajax(request, field_id):
    date_str = request.GET.get("date")

    booking_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

    today = timezone.now().date()
    max_date = today + datetime.timedelta(days=30)

    if booking_date > max_date:
        return JsonResponse({ "error": "Cannot check availability more than 30 days in advance.", "slots": [] }, status=400)
    
    if not Field.objects.filter(pk=field_id).exists():
        return JsonResponse({"error": "Field not found."}, status=404)

    booked_times = set(
        Booking.objects.filter(field_id=field_id, booking_date=booking_date).values_list("start_time", flat=True)
    )
    
    match_times = set(
        Match.objects.filter(
            field_id=field_id, 
            match_date=booking_date, 
            status__in=["Pending", "Confirmed"]
        ).values_list("start_time", flat=True)
    )
    
    unavailable_times = booked_times.union(match_times)
    
    slots = [
        (datetime.time(10, 0), datetime.time(11, 0)),
        (datetime.time(11, 0), datetime.time(12, 0)),
        (datetime.time(12, 0), datetime.time(13, 0)),
        (datetime.time(13, 0), datetime.time(14, 0)),
    ]

    slots_with_status = []
    now_time = timezone.localtime(timezone.now()).time()

    for start, end in slots:
        is_unavailable = start in unavailable_times
        is_past = (booking_date < today) or (booking_date == today and start < now_time)

        status = "available"
        if is_past:
            status = "past"
        elif is_unavailable:
            if start in booked_times:
                status = "booked"
            else:
                status = "match_created"
        
        slots_with_status.append({
            "start": start.strftime("%H:%M"),
            "end": end.strftime("%H:%M"),
            "status": status
        })

    return JsonResponse({ "slots": slots_with_status })
