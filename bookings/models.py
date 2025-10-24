# bookings/models.py
from django.db import models
from django.conf import settings
from fields.models import Field
from django.utils import timezone
from datetime import timedelta

class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Constraint ensures that no two bookings overlap for the same field
        constraints = [
            models.UniqueConstraint(fields=['field', 'booking_date', 'start_time'], name='unique_booking_slot')
        ]
        ordering = ['booking_date', 'start_time']

    def __str__(self):
        return f"Booking for {self.field.name} by {self.user.username} on {self.booking_date} from {self.start_time} to {self.end_time}"

    @property
    def is_past_booking(self):
        """Checks if the booking date and time have passed."""
        now = timezone.now()
        booking_datetime = timezone.make_aware(
            timezone.datetime.combine(self.booking_date, self.end_time)
        )
        return booking_datetime < now

    @staticmethod
    def get_available_slots(field_id, date):
        """
        Returns a list of available time slots for a given field and date.
        Available slots are fixed from 10:00 to 14:00 in 1-hour intervals.
        """
        all_slots = [
            (timezone.datetime.strptime("10:00", "%H:%M").time(), timezone.datetime.strptime("11:00", "%H:%M").time()),
            (timezone.datetime.strptime("11:00", "%H:%M").time(), timezone.datetime.strptime("12:00", "%H:%M").time()),
            (timezone.datetime.strptime("12:00", "%H:%M").time(), timezone.datetime.strptime("13:00", "%H:%M").time()),
            (timezone.datetime.strptime("13:00", "%H:%M").time(), timezone.datetime.strptime("14:00", "%H:%M").time()),
        ]

        booked_slots = Booking.objects.filter(field_id=field_id, booking_date=date).values_list('start_time', flat=True)

        available_slots = []
        for start, end in all_slots:
            if start not in booked_slots:
                available_slots.append({'start': start.strftime("%H:%M"), 'end': end.strftime("%H:%M")})

        return available_slots