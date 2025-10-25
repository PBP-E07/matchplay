from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Tournament, Team, Match
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from datetime import datetime


# Create your views here.
def tournament_list(request):
    status = request.GET.get('status')

    tournaments = Tournament.objects.filter(is_private=False).order_by("-start_date")

    if request.user.is_authenticated:
        user_private = Tournament.objects.filter(is_private=True, created_by=request.user)
        tournaments = (tournaments | user_private).distinct()

    return render(request, 'tournament/list.html', {'tournaments': tournaments})

def tournament_detail(request, pk):
    tournament = get_object_or_404(Tournament, pk=pk)

    if tournament.is_private and tournament.created_by != request.user:
        return render(request, "tournament/access_denied.html", {"tournament": tournament})

    return render(request, 'tournament/detail.html', {'tournament': tournament})

def tournament_matches(request, pk):
    tournament = get_object_or_404(Tournament, pk=pk)

    if tournament.is_private and tournament.created_by != request.user:
        return render(request, "tournament/access_denied.html", {"tournament": tournament})

    return render(request, 'tournament/matches.html', {'tournament': tournament})


def get_tournaments_json(request):
    filter_type = request.GET.get("status")  

    tournaments = Tournament.objects.filter(is_private=False).order_by("-start_date")

    if request.user.is_authenticated:
        user_private = Tournament.objects.filter(is_private=True, created_by=request.user)
        tournaments = (tournaments | user_private).distinct()

    if filter_type == "private" and request.user.is_authenticated:
        tournaments = tournaments.filter(is_private=True, created_by=request.user)
    elif filter_type == "public":
        tournaments = tournaments.filter(is_private=False)

    data = [
        {
            "id": t.id,
            "name": t.name,
            "location": t.location,
            "banner_image": t.banner_image,
            "prize_pool": t.prize_pool,
            "start_date": t.start_date,
            "is_private": t.is_private,
            "total_teams": t.teams.count(),
        }
        for t in tournaments
    ]
    return JsonResponse(data, safe=False)

def get_matches_json(request, pk):
    tournament = get_object_or_404(Tournament, pk=pk)
    matches = tournament.matches.all().order_by('round_number')

    data = [
        {
            "id": m.id,
            "round_number": m.round_number,
            "team1_name": m.team1.name,
            "team1_logo": m.team1.logo_url,
            "team2_name": m.team2.name,
            "team2_logo": m.team2.logo_url,
            "score_team1": m.score_team1,
            "score_team2": m.score_team2,
            "winner_name": m.winner.name if m.winner else None,
            "tournament_id": m.tournament.id,
        }
        for m in matches
    ]
    return JsonResponse(data, safe=False)


def create_tournament(request):
    if request.method == "POST":
        name = request.POST.get("name")
        sport_type = request.POST.get("sport_type")
        location = request.POST.get("location")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        prize_pool = request.POST.get("prize_pool")
        description = request.POST.get("description")
        banner_image = request.POST.get("banner_image")
        is_private = request.POST.get("is_private") == "on"

        if Tournament.objects.filter(name__iexact=name).exists():
            messages.error(request, "Nama turnamen sudah digunakan. Gunakan nama lain.")
            return render(request, "tournament/create_tournament.html")
        
        try:
            if start_date:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            else:
                start_date_obj = timezone.now().date()

            if end_date:
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
                if start_date_obj > end_date_obj:
                    messages.error(request, "Tanggal mulai tidak boleh setelah tanggal selesai.")
                    return render(request, "tournament/create_tournament.html")
            else:
                end_date_obj = None
        except ValueError:
            messages.error(request, "Format tanggal tidak valid.")
            return render(request, "tournament/create_tournament.html")

        prize_pool = prize_pool or None
        if prize_pool:
            if not any(char.isdigit() for char in prize_pool):
                messages.warning(request, "Format hadiah kurang jelas. Contoh: 'Rp 1.000.000'.")


        Tournament.objects.create(
            name=name,
            sport_type=sport_type,
            location=location,
            start_date=start_date or timezone.now().date(),
            end_date=end_date or None,
            prize_pool=prize_pool or None,
            description=description or "",
            banner_image=banner_image or None,
            is_private=is_private,
            created_by=request.user  
        )

        return redirect("tournament:tournament_list")

    return render(request, "tournament/create_tournament.html")


@login_required
def join_tournament(request, pk):
    tournament = get_object_or_404(Tournament, pk=pk)

    if request.method == "POST":
        team_name = request.POST.get("name")
        logo_url = request.POST.get("logo_url")

        if not team_name:
            return render(request, "tournament/join_tournament.html", {
                "tournament": tournament,
                "error": "Nama tim wajib diisi."
            })
        
        if Team.objects.filter(tournament=tournament, name__iexact=team_name).exists():
            return render(request, "tournament/join_tournament.html", {
                "tournament": tournament,
                "error": f"Nama tim '{team_name}' sudah terdaftar di turnamen ini."
            })


        Team.objects.create(
            name=team_name,
            logo_url=logo_url,
            tournament=tournament,
            created_by=request.user 
        )

        tournament.total_teams += 1
        tournament.save()

        return redirect("tournament:tournament_detail", pk=tournament.pk)
    
    return render(request, "tournament/join_tournament.html", {"tournament": tournament})

@login_required 
def edit_tournament(request, pk):
    tournament = get_object_or_404(Tournament, pk=pk)

    if request.method == "POST":
        tournament.name = request.POST.get("name")
        tournament.sport_type = request.POST.get("sport_type")
        tournament.location = request.POST.get("location")
        tournament.prize_pool = request.POST.get("prize_pool") or tournament.prize_pool 

        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        tournament.start_date = start_date or tournament.start_date
        tournament.end_date = end_date or tournament.end_date

        tournament.save()
        print("Updated:", tournament.name, tournament.prize_pool)
        return redirect("tournament:tournament_detail", pk=tournament.pk)

    return render(request, "tournament/edit_tournament.html", {"tournament": tournament})

def delete_tournament(request, pk):
    tournament = get_object_or_404(Tournament, pk=pk)

    if request.method == "POST":
        tournament.delete()
        return redirect("tournament:tournament_list")

    return render(request, "tournament/delete_tournament.html", {"tournament": tournament})


def create_match(request, pk):
    tournament = get_object_or_404(Tournament, pk=pk)
    teams = tournament.teams.all()

    if request.method == "POST":
        team1_id = request.POST.get("team1")
        team2_id = request.POST.get("team2")
        round_number = request.POST.get("round_number")

        if team1_id == team2_id:
            return render(request, "tournament/create_match.html", {
                "tournament": tournament,
                "teams": teams,
                "error": "Tim tidak boleh sama."
            })
        
        try:
            round_number = int(round_number)
            if round_number < 1:
                round_number = 1
        except (TypeError, ValueError):
            round_number = 1  

        team1 = Team.objects.get(id=team1_id)
        team2 = Team.objects.get(id=team2_id)

        Match.objects.create(
            tournament=tournament,
            team1=team1,
            team2=team2,
            round_number=round_number
        )

        print(f"Match created: Round {round_number} - {team1.name} vs {team2.name}")

        return redirect("tournament:tournament_matches", pk=tournament.pk)

    return render(request, "tournament/create_match.html", {
        "tournament": tournament,
        "teams": teams
    })

def edit_match(request, pk, match_id):
    tournament = get_object_or_404(Tournament, pk=pk)
    match = get_object_or_404(Match, pk=match_id, tournament=tournament)

    if request.method == "POST":
        score_team1 = request.POST.get("score_team1")
        score_team2 = request.POST.get("score_team2")

        match.score_team1 = int(score_team1)
        match.score_team2 = int(score_team2)
        match.set_winner_if_done()
        match.save()

        return redirect("tournament:tournament_matches", pk=tournament.pk)

    return render(request, "tournament/edit_match.html", {
        "tournament": tournament,
        "match": match,
    })


def delete_match(request, pk, match_id):
    tournament = get_object_or_404(Tournament, pk=pk)
    match = get_object_or_404(Match, pk=match_id, tournament=tournament)

    if request.method == "POST":
        match.delete()
        return redirect("tournament:tournament_matches", pk=tournament.pk)

    return render(request, "tournament/delete_match.html", {
        "tournament": tournament,
        "match": match
    })
