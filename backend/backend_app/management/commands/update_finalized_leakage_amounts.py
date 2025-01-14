from django.core.management.base import BaseCommand
from backend_app.models import dsoutcome

class Command(BaseCommand):
    help = 'Populate finalized_leakage_amount for existing records'

    def handle(self, *args, **kwargs):
        # Fetch all records that need to be updated
        records = dsoutcome.objects.all()
        print(records)

        # Debugging: Check if records are being fetched
        if not records:
            self.stdout.write("No records found. Please check your database.")
            return

        self.stdout.write(f"Found {len(records)} records to update.")

        updated_count = 0
        for record in records:
            # Debugging: Check if record is not None
            if record is None:
                self.stdout.write("Error: Found a None record, skipping...")
                continue
            
            try:
                # Debugging: Show the record's ID and its fields before saving
                self.stdout.write(f"Leakage Level: {record.leakage_level}, Manual Leakage: {record.manual_leakage_amount}, Potential Leakage: {record.potential_leakage_amount}")

                # Save each record to trigger the overridden save method
                record.save()  # This will call the overridden save() method
                updated_count += 1
                self.stdout.write(f"Finalized Leakage Amount: {record.finalized_leakage_amount}")
            except Exception as e:
                self.stdout.write(f"Error updating record")

        self.stdout.write(f"Total records updated: {updated_count}")
