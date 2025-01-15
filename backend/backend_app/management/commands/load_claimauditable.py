# filepath: /C:/Users/digvijay221046/Desktop/Git-AG-DJ/dashboards_/backend/backend_app/management/commands/load_claimauditable.py
import csv
import random
from django.core.management.base import BaseCommand
from backend_app.models import ClaimAuditable, Claims, Parameter
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

        ClaimAuditable.objects.all().delete()
        print("All data deleted for ClaimAuditable")

        # Get all claims and parameters for random selection
        all_claims = list(Claims.objects.all())
        all_parameters = list(Parameter.objects.all())
        
        substitutions = {'claims': [], 'parameters': []}

        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            print("CSV Headers:", reader.fieldnames)
            
            for row in reader:
                try:
                    # Get or substitute claim
                    try:
                        claim = Claims.objects.get(claim_id=row['claim_id'])
                    except Claims.DoesNotExist:
                        claim = random.choice(all_claims) if all_claims else None
                        if claim:
                            substitutions['claims'].append((row['claim_id'], claim.claim_id))

                    # Get or substitute parameter
                    try:
                        parameter = Parameter.objects.get(parameter_id=row['parameter_id'])
                    except Parameter.DoesNotExist:
                        parameter = random.choice(all_parameters) if all_parameters else None
                        if parameter:
                            substitutions['parameters'].append((row['parameter_id'], parameter.parameter_id))

                    if claim and parameter:
                        ClaimAuditable.objects.create(
                            claim=claim,
                            parameter=parameter,
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

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error processing row: {str(e)}"))

        # Report substitutions
        if substitutions['claims']:
            self.stdout.write("\nClaim substitutions made:")
            for original, substitute in substitutions['claims']:
                self.stdout.write(f"Original: {original} -> Substitute: {substitute}")

        if substitutions['parameters']:
            self.stdout.write("\nParameter substitutions made:")
            for original, substitute in substitutions['parameters']:
                self.stdout.write(f"Original: {original} -> Substitute: {substitute}")

        self.stdout.write(self.style.SUCCESS('Successfully loaded data from "%s"' % csv_file))