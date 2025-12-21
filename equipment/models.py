from django.db import models

from django.db import models

class Equipment(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='equipment_images/', blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    @property
    def get_image_url(self):
        if self.image:
            # Jika isinya link internet (dataset), langsung balikin linknya
            if str(self.image).startswith('http'):
                return self.image
            # Jika isinya file upload lokal, pake .url standar
            return self.image.url
        return "https://via.placeholder.com/400" # Gambar cadangan

class Rental(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    renter_name = models.CharField(max_length=100)
    quantity_rented = models.PositiveIntegerField(default=1) # Tambahkan ini
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        duration_hours = (self.end_time - self.start_time).total_seconds() / 3600
        # Sekarang harga dikalikan dengan jumlah alat yang disewa
        self.total_cost = duration_hours * float(self.equipment.price_per_hour) * self.quantity_rented
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.renter_name} - {self.equipment.name}"
