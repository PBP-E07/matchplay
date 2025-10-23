from django.core.management.base import BaseCommand
from fields.models import Field
import json

class Command(BaseCommand):
    help = 'Import fields data from JSON file'

    def handle(self, *args, **kwargs):
        with open('fields/data/fields.json', 'r') as f:
            data = json.load(f)

        categories = sorted(set(item['sport'].strip().title() for item in data))

        for item in categories:
            print(f"('{item.lower()}', '{item}'),")