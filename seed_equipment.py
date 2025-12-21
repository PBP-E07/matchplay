import os
import django
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'matchplay.settings')
django.setup()

from equipment.models import Equipment

def run_seed():
    names = ["Bola Basket Spalding", "Raket Yonex", "Jersey Retro", "Sarung Tangan Kiper", "Matras Yoga"]
    images = [
        "https://images.unsplash.com/photo-1546519638-68e109498ffc",
        "https://images.unsplash.com/photo-1626225967045-9c730a0a06bb",
        "https://images.unsplash.com/photo-1574629810360-7efbbe195018",
        "https://images.unsplash.com/photo-1518770660439-4636190af475",
        "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b"
    ]

    for i in range(10):  # Mau nambahin berapa banyak?
        name = random.choice(names) + f" Gen-{i}"
        Equipment.objects.create(
            name=name,
            quantity=random.randint(1, 20),
            price_per_hour=random.choice([15000, 25000, 35000, 50000]),
            description=f"Deskripsi otomatis untuk {name}. Alat olahraga kualitas terbaik.",
            # Untuk testing, kita bisa simpan URL string di ImageField 
            # (Tapi di Flutter nanti harus pakai Image.network)
            image=random.choice(images) 
        )
    print("Berhasil menambahkan dataset!")

if __name__ == "__main__":
    run_seed()