from django.db import models
from django.conf import settings
from fields.models import Field
from bookings.models import Booking # Import Booking to check availability
from django.core.exceptions import ValidationError
from django.utils import timezone
import datetime

class Match(models.Model):
    """Represents a matchmaking room created by a user."""

    LEVEL_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
        ('All Levels', 'All Levels'),
    ]
    STATUS_CHOICES = [
        ('Pending', 'Pending'), # Waiting for players
        ('Confirmed', 'Confirmed'), # Enough players joined, or manually confirmed
        ('Completed', 'Completed'), # Match time has passed
        ('Cancelled', 'Cancelled'), # Cancelled by organizer or system
    ]

    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organized_matches'
    )
    field = models.ForeignKey(
        Field,
        on_delete=models.CASCADE,
        related_name='matches'
    )
    sport = models.CharField(max_length=50, editable=False) # Will be derived from field
    match_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    skill_level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='All Levels')
    max_players = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True, help_text="Add any extra details, e.g., 'Mixed skill levels, just have fun!'")
    price_per_person = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    # Use through=MatchPlayer for the many-to-many relationship
    players = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='MatchPlayer',
        related_name='joined_matches',
        blank=True
    )

    def __str__(self):
        return f"{self.get_sport_display()} Match at {self.field.name} on {self.match_date} ({self.start_time.strftime('%H:%M')})"

    def save(self, *args, **kwargs):
        # Automatically set sport based on the field
        if self.field:
            self.sport = self.field.get_sport_display() # Use the display name
        super().save(*args, **kwargs)

    @property
    def current_player_count(self):
        """Returns the number of players currently joined (including organizer)."""
        # Count distinct players associated via MatchPlayer
        return self.matchplayer_set.count()

    @property
    def spots_left(self):
        """Calculates the number of spots remaining."""
        return max(0, self.max_players - self.current_player_count)

    @property
    def is_full(self):
        """Checks if the match has reached its maximum player capacity."""
        return self.current_player_count >= self.max_players

    @property
    def is_past_match(self):
        """Checks if the match date and end time have passed."""
        now = timezone.now()
        match_end_datetime = timezone.make_aware(
            datetime.datetime.combine(self.match_date, self.end_time)
        )
        return match_end_datetime < now

    def is_venue_booked(self):
        """Checks if the venue is already booked via the bookings app for the same time."""
        # Check for any booking that starts exactly at the same time for this field and date
        return Booking.objects.filter(
            field=self.field,
            booking_date=self.match_date,
            start_time=self.start_time
        ).exists()

    def clean(self):
        """Custom validation for the model."""
        super().clean()
        # 1. Check end_time is after start_time
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time.")

        # 2. Check match date is not in the past
        if self.match_date and self.match_date < timezone.now().date():
             raise ValidationError("Cannot create a match for a past date.")
        elif self.match_date == timezone.now().date() and self.start_time <= timezone.now().time():
             raise ValidationError("Cannot create a match for a past time.")

        # 3. Check if the venue is already booked (important!)
        if self.field and self.match_date and self.start_time:
            if self.is_venue_booked():
                raise ValidationError(f"The selected time slot ({self.start_time.strftime('%H:%M')}) for {self.field.name} on {self.match_date} is already booked.")

        # 4. Check max_players is at least 2 (or 1 if organizer counts?)
        if self.max_players < 2:
             raise ValidationError("Maximum players must be at least 2.")


    class Meta:
        ordering = ['match_date', 'start_time']
        verbose_name = "Match"
        verbose_name_plural = "Matches"

    @property
    def progress_percentage(self):
        """Calculates the fill percentage for the progress bar."""
        if not self.max_players or self.max_players == 0:
            return 0
        # Calculate percentage and ensure it doesn't exceed 100
        percentage = (self.current_player_count / self.max_players) * 100
        return min(percentage, 100)


class MatchPlayer(models.Model):
    """Intermediate model for the Match-User relationship."""
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('match', 'user') # Prevent a user joining the same match twice
        ordering = ['joined_at']

    def __str__(self):
        return f"{self.user.username} joined {self.match.field.name} on {self.match.match_date}"
