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

    def is_venue_match_conflict(self):
        """Checks if the venue is already taken by another match for the same time."""
        # Check for any *other* match (excluding self)
        return Match.objects.filter(
            field=self.field,
            match_date=self.match_date,
            start_time=self.start_time
        ).exclude(pk=self.pk).exists()

    def clean(self):
        """Custom validation for the model."""
        super().clean()
        # 1. Check end_time is after start_time
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time.")

        # 2. Check match date is not in the past
        if self.match_date and self.match_date < timezone.now().date():
             raise ValidationError("Cannot create a match for a past date.")
        # --- MODIFIED CHECK ---
        # Check that self.start_time is not None before comparing
        elif self.match_date == timezone.now().date() and self.start_time and self.start_time <= timezone.now().time():
             raise ValidationError("Cannot create a match for a past time.")

        # 3. Check if the venue is already booked (important!)
        # This block will only run if all self.x values are not None
        if self.field and self.match_date and self.start_time:
            if self.is_venue_booked():
                raise ValidationError(f"The selected time slot ({self.start_time.strftime('%H:%M')}) for {self.field.name} on {self.match_date} is already booked directly.")
            
            # 4. NEW: Check for match conflicts
            if self.is_venue_match_conflict():
                 raise ValidationError(f"The selected time slot ({self.start_time.strftime('%H:%M')}) for {self.field.name} on {self.match_date} is already taken by another match.")

        # 5. Check max_players
        if self.max_players is not None and self.max_players < 2:
             raise ValidationError("Maximum players must be at least 2.")
        elif self.max_players is None:
             raise ValidationError("Maximum players must be set.")

    @staticmethod
    def get_all_slots_status(field_id, date):
        """
        Checks both Bookings and Matches for the fixed time slots.
        Returns a list of all time slots (10:00-14:00) and their status.
        """
        all_slots = [
            (datetime.time(10, 0), datetime.time(11, 0)),
            (datetime.time(11, 0), datetime.time(12, 0)),
            (datetime.time(12, 0), datetime.time(13, 0)),
            (datetime.time(13, 0), datetime.time(14, 0)),
        ]
        
        if not field_id or not date:
             # Return all as 'unavailable' if key info is missing
             return [
                {
                    'start': start.strftime("%H:%M"),
                    'end': end.strftime("%H:%M"),
                    'status': 'unavailable',
                    'message': 'Invalid field or date'
                } for start, end in all_slots
            ]

        # 1. Get booked slots from 'bookings' app
        booked_start_times = set(Booking.objects.filter(
            field_id=field_id,
            booking_date=date
        ).values_list('start_time', flat=True))

        # 2. Get taken slots from 'matches' app
        match_start_times = set(Match.objects.filter(
            field_id=field_id,
            match_date=date,
            status__in=['Pending', 'Confirmed'] # Only check for active matches
        ).values_list('start_time', flat=True))

        slots_with_status = []
        for start, end in all_slots:
            status = 'available'
            message = 'Available'
            if start in booked_start_times:
                status = 'booked'
                message = 'Booked'
            elif start in match_start_times:
                status = 'match_created'
                message = 'Match Created'

            slots_with_status.append({
                'start': start.strftime("%H:%M"),
                'end': end.strftime("%H:%M"),
                'status': status # 'available', 'booked', or 'match_created'
            })
        return slots_with_status


    class Meta:
        ordering = ['match_date', 'start_time']
        verbose_name = "Match"
        verbose_name_plural = "Matches"


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
