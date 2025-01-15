# filepath: /C:/Users/digvijay221046/Desktop/Git-AG-DJ/dashboards_/backend/backend_app/management/commands/load_claim_notes.py
import csv
from django.core.management.base import BaseCommand
from backend_app.models import ClaimNotes

class Command(BaseCommand):
    help = 'Load claim notes data from CSV file into the database'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file to be loaded')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        # Delete previous data
        ClaimNotes.objects.all().delete()
        self.stdout.write(self.style.WARNING('Deleted previous data from ClaimNotes model'))

        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                ClaimNotes.objects.create(
                    claim_id=row['claim_id'],
                    department=row['department'],
                    group_name=row['group_name'],
                    update_date=row['update_date']
                )

        self.stdout.write(self.style.SUCCESS('Successfully loaded data from "%s"' % csv_file))