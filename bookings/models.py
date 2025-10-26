from django.db import models
from django.conf import settings
from fields.models import Field

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
        ordering = ["booking_date", "start_time"] # Order bookings chronologically

    def __str__(self):
        return f"Booking for {self.field.name} by {self.user.username} on {self.booking_date} at {self.start_time.strftime('%H:%M')}"
