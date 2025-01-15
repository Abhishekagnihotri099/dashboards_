# filepath: /C:/Users/digvijay221046/Desktop/Git-AG-DJ/dashboards_/backend/backend_app/management/commands/load_distribution_channel.py
import csv
from django.core.management.base import BaseCommand
from backend_app.models import policy

class Command(BaseCommand):
    help = 'Load distribution channel data from CSV file into the database'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file to be loaded')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        # Delete previous data
        policy.objects.all().delete()
        self.stdout.write(self.style.WARNING('Deleted previous data from DistributionChannel model'))

        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                policy.objects.create(
                    policy_id=row['policy_id'],
                    distribution_channel=row['distribution_channel']
                )

        self.stdout.write(self.style.SUCCESS('Successfully loaded data from "%s"' % csv_file))