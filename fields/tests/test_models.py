from django.test import TestCase
from fields.models import Field, Facility

class FacilityModelTest(TestCase):
    def test_str_returns_name(self):
        facility = Facility.objects.create(name="Toilet")
        self.assertEqual(str(facility), "Toilet")


class FieldModelTest(TestCase):
    def setUp(self):
        self.facility1 = Facility.objects.create(name="Lampu")
        self.facility2 = Facility.objects.create(name="Tempat Duduk")

    def test_create_field_and_str(self):
        field = Field.objects.create(
            name="Lapangan Futsal A",
            image="https://example.com/futsal.jpg",
            price=100000,
            rating=4.7,
            location="Jakarta",
            sport="futsal",
            url="https://example.com",
        )
        field.facilities.add(self.facility1, self.facility2)
        self.assertEqual(str(field), "Lapangan Futsal A")

    def test_rating_validator(self):
        from django.core.exceptions import ValidationError

        field = Field(
            name="Lapangan Gagal",
            image="img.jpg",
            price=50000,
            rating=6.0,  # invalid
            location="Bandung",
            sport="futsal",
            url="https://example.com",
        )
        with self.assertRaises(ValidationError):
            field.full_clean()