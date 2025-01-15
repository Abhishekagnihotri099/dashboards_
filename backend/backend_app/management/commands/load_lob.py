# filepath: /C:/Users/digvijay221046/Desktop/Git-AG-DJ/dashboards_/backend/backend_app/management/commands/load_lob.py
import csv
from django.core.management.base import BaseCommand
from backend_app.models import LOB

class Command(BaseCommand):
    help = 'Load LOB data from CSV file into the database'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file to be loaded')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        # Delete previous data
        LOB.objects.all().delete()
        self.stdout.write(self.style.WARNING('Deleted previous data from LOB model'))

        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                LOB.objects.create(
                    lob=row['LOB'],
                    line_of_business=row['Line Of Business']
                )

        self.stdout.write(self.style.SUCCESS('Successfully loaded data from "%s"' % csv_file))