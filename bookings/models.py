from django.db import models
from django.conf import settings
from fields.models import Field
from django.utils import timezone
import datetime

class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["field", "booking_date", "start_time"], name="unique_booking_slot")
        ]

        ordering = ["booking_date", "start_time"]

    def __str__(self):
        return f"Booking for { self.field.name } by { self.user.username } on { self.booking_date }"

    @property
    def is_past_booking(self):
        now = timezone.now()

        booking_end_datetime = timezone.make_aware(
            timezone.datetime.combine(self.booking_date, self.end_time)
        )
        
        return booking_end_datetime < now

    @staticmethod
    def get_available_slots(field_id, date):
        all_slots = [
            (datetime.time(10, 0), datetime.time(11, 0)),
            (datetime.time(11, 0), datetime.time(12, 0)),
            (datetime.time(12, 0), datetime.time(13, 0)),
            (datetime.time(13, 0), datetime.time(14, 0)),
        ]
        booked_start_times = set(Booking.objects.filter(field_id=field_id, booking_date=date).values_list("start_time", flat=True))

        available_slots = []

        for start, end in all_slots:
            if start not in booked_start_times:
                available_slots.append({"start": start.strftime("%H:%M"), "end": end.strftime("%H:%M")})

        return available_slots

    @staticmethod
    def get_all_slots_status(field_id, date):
        all_slots = [
            (datetime.time(10, 0), datetime.time(11, 0)),
            (datetime.time(11, 0), datetime.time(12, 0)),
            (datetime.time(12, 0), datetime.time(13, 0)),
            (datetime.time(13, 0), datetime.time(14, 0)),
        ]
        
        booked_start_times = set(Booking.objects.filter(field_id=field_id, booking_date=date).values_list("start_time", flat=True))

        slots_with_status = []

        for start, end in all_slots:
            is_booked = start in booked_start_times
            slots_with_status.append({
                "start": start.strftime("%H:%M"),
                "end": end.strftime("%H:%M"),
                "is_booked": is_booked
            })

        return slots_with_status
