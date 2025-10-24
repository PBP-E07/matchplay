from django.db import models
from django.contrib.auth.models import User

class Tournament(models.Model):
    name = models.CharField(max_length=120)
    sport_type = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    banner_image = models.URLField(null=True, blank=True)
    description = models.TextField(blank=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True, blank=True)
    prize_pool = models.CharField(max_length=100, blank=True)
    total_teams = models.PositiveIntegerField(default=0)
    is_private = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tournaments", null=True, blank=True)

    def __str__(self):
        return self.name


class Team(models.Model):
    name = models.CharField(max_length=100)
    logo_url = models.URLField(blank=True, null=True)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name="teams")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    eliminated = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.tournament.name})"
    
class Match(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='matches')
    round_number = models.PositiveIntegerField(default=1)
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='as_team1')
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='as_team2')
    score_team1 = models.IntegerField(null=True, blank=True)
    score_team2 = models.IntegerField(null=True, blank=True)
    winner = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='wins')

    def set_winner_if_done(self):
        if self.score_team1 is not None and self.score_team2 is not None:
            self.winner = self.team1 if self.score_team1 > self.score_team2 else self.team2
            self.save()

    