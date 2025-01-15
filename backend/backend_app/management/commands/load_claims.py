from django.core.management.base import BaseCommand
from backend_app.models import Claims, LOB
from django.utils.dateparse import parse_date
import csv

class Command(BaseCommand):
    help = 'Load data from claims.csv into Claims model'

    def handle(self, *args, **kwargs):
        Claims.objects.all().delete()
        print("All claims deleted")
        
        csv_file_path = 'backend_app/claims_0.1.csv'
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    # Get existing LOB instance
                    lob_instance = LOB.objects.get(lob=row['lob'])
                    
                    Claims.objects.create(
                        claim_id=row['claim_id'],
                        policy_id=row['policy_id'],
                        general_nature_of_loss=row['general_nature_of_loss'],
                        loss_claim_cause=row['loss_claim_cause'],
                        lob=lob_instance,  # Use LOB instance instead of string
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
                except LOB.DoesNotExist:
                    print(f"LOB {row['lob']} not found")
                except Exception as e:
                    print(f"Error processing claim {row['claim_id']}: {str(e)}")

        self.stdout.write(self.style.SUCCESS('Successfully loaded claims data'))