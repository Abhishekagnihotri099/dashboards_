# filepath: /C:/Users/digvijay221046/Desktop/Git-AG-DJ/dashboards_/backend/backend_app/management/commands/generate_claims_csv.py
import csv
import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from backend_app.models import Claims

class Command(BaseCommand):
    help = 'Generate a CSV file with claim_id, department, group_name, and update_date'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file to be generated')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        departments = ['GT Automation Platform','DIA DC & IIA IC Settlements/Recoveries - WNS RCA' , 'DIA DC Recovery Ops, Agent & Salvage' , 'AUD LTC Common Functions & Operations Support' , 'AUD CD PS Underwriting','AUD OP WNS - Training']
        group_names = ['Motor CGU Broker Strategic Partners Attributes', 'Property Claims CGU Broker VIC/TAS - Level 3' , 'IIA P&S Rapid CGU' , 'Peoples Choice - Motor  - level 2' , 'Motor WFI National WA - Level 1' , 'Major Events Property Claims CGU Broker']

        def random_date(start, end):
            return start + timedelta(
                seconds=random.randint(0, int((end - start).total_seconds())),
            )

        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 31)

        with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['claim_id', 'department', 'group_name', 'update_date'])

            for claim in Claims.objects.all():
                department = random.choice(departments)
                group_name = random.choice(group_names)
                update_date = random_date(start_date, end_date).strftime('%Y-%m-%d')

                writer.writerow([claim.claim_id, department, group_name, update_date])

        self.stdout.write(self.style.SUCCESS('Successfully generated CSV file at "%s"' % csv_file))