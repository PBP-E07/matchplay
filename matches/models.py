from django.db import models
from django.conf import settings
from fields.models import Field

class Match(models.Model):
    LEVEL_CHOICES = [
        ("Beginner", "Beginner"),
        ("Intermediate", "Intermediate"),
        ("Advanced", "Advanced"),
        ("All Levels", "All Levels"),
    ]

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Confirmed", "Confirmed"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
    ]

    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organized_matches"
    )
    field = models.ForeignKey(
        Field,
        on_delete=models.CASCADE,
        related_name="matches"
    )
    sport = models.CharField(max_length=50, editable=False)
    match_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    skill_level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default="All Levels")
    max_players = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)
    price_per_person = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)
    players = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="MatchPlayer",
        related_name="joined_matches",
        blank=True
    )

    def __str__(self):
        return f"{self.get_sport_display()} Match at {self.field.name} on {self.match_date} ({self.start_time.strftime("%H:%M")})"

    def save(self, *args, **kwargs):
        if self.field:
            self.sport = self.field.get_sport_display()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["match_date", "start_time"]
        verbose_name = "Match"
        verbose_name_plural = "Matches"


class MatchPlayer(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("match", "user")
        ordering = ["joined_at"]

    def __str__(self):
        return f"{self.user.username} joined {self.match.field.name} on {self.match.match_date}"
