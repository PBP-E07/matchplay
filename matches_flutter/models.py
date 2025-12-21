from django.db import models
from django.contrib.auth.models import User

from fields.models import Field

class Match(models.Model):
    TIME_SLOTS = [
        ("10.00-11.00", "10.00 - 11.00"),
        ("11.00-12.00", "11.00 - 12.00"),
        ("12.00-13.00", "12.00 - 13.00"),
        ("13.00-14.00", "13.00 - 14.00"),
    ]

    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    time_slot = models.CharField(max_length=20, choices=TIME_SLOTS)
    
    price = models.IntegerField(default=0)
    current_players = models.IntegerField(default=1)
    max_players = models.IntegerField(default=10)

    @property
    def spots_left(self):
        return self.max_players - self.current_players

    @property
    def progress(self):
        if self.max_players == 0: return 0
        return self.current_players / self.max_players

    def __str__(self):
        return f"{self.field.name} ({self.time_slot})"
    