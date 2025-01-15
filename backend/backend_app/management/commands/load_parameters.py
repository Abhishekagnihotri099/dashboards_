from django.core.management.base import BaseCommand
from backend_app.models import Parameter
from django.utils.dateparse import parse_datetime
import csv

class Command(BaseCommand):
    help = 'Load data from parameter.csv into Parameter model'

    def handle(self, *args, **kwargs):
        Parameter.objects.all().delete()
        self.stdout.write("All parameters deleted")
        
        csv_file_path = 'backend_app/parameters_0.1.csv'
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    Parameter.objects.create(
                        parameter_id=row['parameter_id'],
                        operationalised_flag=row['operationalised_flag'] if row['operationalised_flag'] != 'NULL' else None,
                        operationalised_status=row['operationalised_status'] if row['operationalised_status'] != 'NULL' else None,
                        other_subparameter_id=row['other_subparameter_id'] if row['other_subparameter_id'] != 'NULL' else None,
                        subtype_name=row['subtype_name'] if row['subtype_name'] != 'NULL' else None,
                        type_code=row['type_code'] if row['type_code'] != 'NULL' else None,
                        type_end_date=parse_datetime(row['type_end_date']) if row['type_end_date'] != 'NULL' else None,
                        type_name=row['type_name'] if row['type_name'] != 'NULL' else None,
                        type_start_date=parse_datetime(row['type_start_date']) if row['type_start_date'] != 'NULL' else None,
                        type_status=row['type_status'] if row['type_status'] != 'NULL' else None,
                        type_value=row['type_value'] if row['type_value'] != 'NULL' else None,
                        compliance_flag=row['compliance_flag'] if row['compliance_flag'] != 'NULL' else None,
                        component_of_claim=row['component_of_claim'] if row['component_of_claim'] != 'NULL' else None,
                        customer_experience_flag=row['customer_experience_flag'] if row['customer_experience_flag'] != 'NULL' else None,
                        data_integrity_flag=row['data_integrity_flag'] if row['data_integrity_flag'] != 'NULL' else None,
                        leakage_flag=row['leakage_flag'] if row['leakage_flag'] != 'NULL' else None,
                        indicator_name=row['indicator_name'] if row['indicator_name'] != 'NULL' else None,
                        line_of_business=row['line_of_business'] if row['line_of_business'] != 'NULL' else None,
                        parameter_end_date=parse_datetime(row['parameter_end_date']) if row['parameter_end_date'] != 'NULL' else None,
                        parameter_no=int(row['parameter_no']) if row['parameter_no'] != 'NULL' else None,
                        parameter_stage=row['parameter_stage'] if row['parameter_stage'] != 'NULL' else None,
                        parameter_start_date=parse_datetime(row['parameter_start_date']) if row['parameter_start_date'] != 'NULL' else None,
                        parameter_status=row['parameter_status'] if row['parameter_status'] != 'NULL' else None,
                        parameter_type=row['parameter_type'] if row['parameter_type'] != 'NULL' else None,
                        parameter_weightage=int(row['parameter_weightage']) if row['parameter_weightage'] != 'NULL' else None,
                        phase_name=row['phase_name'] if row['phase_name'] != 'NULL' else None,
                        policy_review_flag=row['policy_review_flag'] if row['policy_review_flag'] != 'NULL' else None,
                        question=row['question'] if row['question'] != 'NULL' else None,
                        sampling_methodology=row['sampling_methodology'] if row['sampling_methodology'] != 'NULL' else None,
                        signal_id=row['signal_id'] if row['signal_id'] != 'NULL' else None,
                        signal_level=row['signal_level'] if row['signal_level'] != 'NULL' else None,
                        source_system=row['source_system'] if row['source_system'] != 'NULL' else None,
                        triggers=row['triggers'] if row['triggers'] != 'NULL' else None,
                        unit_of_measurement=row['unit_of_measurement'] if row['unit_of_measurement'] != 'NULL' else None,
                        subparameter_description=row['subparameter_description'] if row['subparameter_description'] != 'NULL' else None,
                        subparameter_id=row['subparameter_id'] if row['subparameter_id'] != 'NULL' else None
                    )
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error processing parameter {row['parameter_id']}: {str(e)}"))

        self.stdout.write(self.style.SUCCESS('Successfully loaded parameter data'))