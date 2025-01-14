# filepath: /C:/Users/digvijay221046/Desktop/Git-AG-DJ/dashboards_/backend/backend_app/management/commands/load_claimauditable.py
import csv
import random
from django.core.management.base import BaseCommand
from backend_app.models import ClaimAuditable, Claims
from datetime import datetime

class Command(BaseCommand):
    help = 'Load ClaimAuditable data from CSV file into the database'

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
        ClaimAuditable.objects.all().delete()
        # dsoutcome.objects.all().delete()
        print("All data deleted for DSoutcome")
        self.stdout.write(self.style.WARNING('Deleted previous data from ClaimAuditable model'))

        # Get all claims for random selection
        all_claims = list(Claims.objects.all())
        # csv_file = 'backend_app/claimauditable_0.1.csv'
        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            print("CSV Headers:", reader.fieldnames)
            for row in reader:
                try:
                    claim = Claims.objects.get(claim_id=row['claim_id'])
                except Claims.DoesNotExist:
                    claim = random.choice(all_claims) if all_claims else None
                    self.stdout.write(self.style.WARNING(f"Claim with claim_id {row['claim_id']} does not exist. Using random claim_id {claim.claim_id if claim else 'None'}"))

                if claim:
                    ClaimAuditable.objects.create(
                        claim=claim,
                        parameter_id=row['parameter_id'],
                        parameter_score=row['parameter_score'] if row['parameter_score'] != 'NULL' else None,
                        parameter_score_ai=row['parameter_score_ai'] if row['parameter_score_ai'] != 'NULL' else None,
                        audit_date=parse_date(row['audit_date']),
                        parameter_name=row['parameter_name'] if row['parameter_name'] != 'NULL' else None,
                        due_date=parse_date(row['due_date']),
                        final_audit_status=row['final_audit_status'] if row['final_audit_status'] != 'NULL' else None,
                        parameter_audit_date=parse_date(row['parameter_audit_date']),
                        lob=row['lob'] if row['lob'] != 'NULL' else None,
                        final_lob=row['final_lob'] if row['final_lob'] != 'NULL' else None,
                        parameter_comments=row['parameter_comments'] if row['parameter_comments'] != 'NULL' else None
                    )

        self.stdout.write(self.style.SUCCESS('Successfully loaded data from "%s"' % csv_file))