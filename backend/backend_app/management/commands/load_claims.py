
import csv
from django.core.management.base import BaseCommand
from backend_app.models import Claims
from datetime import datetime

class Command(BaseCommand):
    help = 'Load claims data from CSV file into the database'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file to be loaded')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        def parse_date(date_str):
            if date_str in ["NULL", ""]:
                return None
            try:
                return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return datetime.strptime(date_str, '%Y-%m-%d')

        # Delete previous data
        Claims.objects.all().delete()
        self.stdout.write(self.style.WARNING('Deleted previous data from Claims model'))

        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                Claims.objects.create(
                    claim_id=row['claim_id'],
                    policy_id=row['policy_id'],
                    general_nature_of_loss=row['general_nature_of_loss'],
                    loss_claim_cause=row['loss_claim_cause'],
                    lob=row['lob'],
                    loss_date=parse_date(row['loss_date']),
                    close_date=parse_date(row['close_date']),
                    claim_status=row['claim_status'],
                    claim_owner_first_name=row['claim_owner_first_name'],
                    claim_owner_last_name=row['claim_owner_last_name'],
                    remaining_reserve=float(row['remaining_reserve']) if row['remaining_reserve'] not in ["NULL", ""] else None,
                    paid_amount=float(row['paid_amount']) if row['paid_amount'] not in ["NULL", ""] else None,
                    total_recovery=float(row['total_recovery']) if row['total_recovery'] not in ["NULL", ""] else None,
                    location_state=row['location_state'],
                    audit_date=parse_date(row['audit_date']),
                )

        self.stdout.write(self.style.SUCCESS('Successfully loaded data from "%s"' % csv_file))