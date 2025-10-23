# myapp/management/commands/import_fields.py
from django.core.management.base import BaseCommand
from fields.models import Field, Facility
import json

class Command(BaseCommand):
    help = 'Import fields data from JSON file'

    def handle(self, *args, **kwargs):
        with open('fields/data/fields.json', 'r') as f:
            data = json.load(f)

        for item in data:
            # Buat field tanpa facilities
            field_obj = Field.objects.create(
                name = item['name'],
                image = item['image'],
                price = item['price'],
                rating = float(item['rating']),
                location = item['location'][2:],
                sport = item['sport'].lower(),
                url = item['url']
            )

            # Tambahkan facilities sebagai ManyToMany
            for fac_name in item.get('facilities', []):
                fac_obj, created = Facility.objects.get_or_create(name=fac_name)
                field_obj.facilities.add(fac_obj)

        self.stdout.write(self.style.SUCCESS('Successfully imported fields'))
