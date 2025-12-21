from django.utils import timezone
from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpResponse
from fields.models import Field
from django.db.models import Q
from matches.models import Match


def show_main(request):
    query = request.GET.get("q", "")
    
    if query:
        field_list = Field.objects.filter(
            Q(name__icontains=query) | 
            Q(location__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()
    else:
        field_list = Field.objects.all().order_by("name")

    now = timezone.now()
    available_matches_qs = Match.objects.filter(
        status="Pending",
        match_date__gte=now.date()
    ).exclude(
        match_date=now.date(), end_time__lte=now.time()
    ).select_related("organizer", "field").prefetch_related("matchplayer_set")

    if query:
        available_matches_qs = available_matches_qs.filter(
            Q(field__name__icontains=query) |
            Q(sport__icontains=query) |
            Q(field__location__icontains=query)
        ).distinct()

    matches_to_display = []
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

    context = {
        "fields": field_list,
        "matches": matches_to_display,
        "query": query
    }

    return render(request, "main.html", context)

def search_fields(request):
    query = request.GET.get("q", "")
    
    if query:
        field_list = Field.objects.filter(
            Q(name__icontains=query) | 
            Q(location__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()
    else:
        field_list = Field.objects.all().order_by("name")

    context = {
        "field_list": field_list,
        "request": request,
    }
    
    html = render_to_string("partials/field_list_content.html", context)
    
    return HttpResponse(html)

def search_matches(request):
    query = request.GET.get("q", "")

    now = timezone.now()
    available_matches_qs = Match.objects.filter(
        status="Pending",
        match_date__gte=now.date()
    ).exclude(
        match_date=now.date(), end_time__lte=now.time()
    ).select_related("organizer", "field").prefetch_related("matchplayer_set")

    if query:
        available_matches_qs = available_matches_qs.filter(
            Q(field__name__icontains=query) |
            Q(sport__icontains=query) |
            Q(field__location__icontains=query)
        ).distinct()

    matches_to_display = []
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

    context = {
        "matches": matches_to_display,
        "user": request.user,
    }
    
    html = render_to_string("partials/match_list_content.html", context)
    
    return HttpResponse(html)
