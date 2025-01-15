# filepath: /C:/Users/digvijay221046/Desktop/Git-AG-DJ/dashboards_/backend/backend_app/management/commands/generate_distribution_channel_csv.py
import csv
import random
from django.core.management.base import BaseCommand
from backend_app.models import Claims

class Command(BaseCommand):
    help = 'Generate a CSV file with policy_id and distribution_channel'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file to be generated')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        distribution_channels = ['5102', '5101', '1101', '5122', '2122']

        with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['policy_id', 'distribution_channel'])

            for claim in Claims.objects.all():
                distribution_channel = random.choice(distribution_channels)
                writer.writerow([claim.policy_id, distribution_channel])

        self.stdout.write(self.style.SUCCESS('Successfully generated CSV file at "%s"' % csv_file))