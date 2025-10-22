from django.db import models

class Field(models.Model):
    SPORT_CATEGORY = [
        ('badminton', 'Badminton'),
        ('basketball', 'Basketball'),
        ('billiard', 'Billiard'),
        ('e-sport', 'E-Sport'),
        ('futsal', 'Futsal'),
        ('golf', 'Golf'),
        ('mini soccer', 'Mini Soccer'),
        ('padel', 'Padel'),
        ('pickleball', 'Pickleball'),
        ('sepak bola', 'Sepak Bola'),
        ('squash', 'Squash'),
        ('tenis meja', 'Tenis Meja'),
        ('tennis', 'Tennis')
    ]

    name = models.CharField(max_length=100)
    image = models.CharField(max_length=200)
    price = models.PositiveIntegerField()
    rating = models.CharField(max_length=5)
    location = models.CharField(max_length=200)
    sport = models.CharField(max_length=20, choices=SPORT_CATEGORY)
    facilities = models.JSONField(default=list)
    url = models.CharField(max_length=200)

    def __str__(self):
        return self.name