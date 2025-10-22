from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Facility(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
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
    rating = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    location = models.CharField(max_length=200)
    sport = models.CharField(max_length=20, choices=SPORT_CATEGORY)
    facilities = models.ManyToManyField(Facility, blank=True)
    url = models.CharField(max_length=200)

    def __str__(self):
        return self.name