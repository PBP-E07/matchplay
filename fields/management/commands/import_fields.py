# myapp/management/commands/import_fields.py
from django.core.management.base import BaseCommand
from fields.models import Field
import json

class Command(BaseCommand):
    help = 'Import fields data from JSON file'

    def handle(self, *args, **kwargs):
        with open('fields/data/fields.json', 'r') as f:
            data = json.load(f)

        for item in data:
            Field.objects.create(
                name = item['name'],
                image = item['image'],
                price = item['price'],
                rating = item['rating'],
                location = item['location'][2:],
                sport = item['sport'].lower(),
                facilities = item.get('facilities', []),
                url = item['url']
            )

        self.stdout.write(self.style.SUCCESS('Successfully imported fields'))
