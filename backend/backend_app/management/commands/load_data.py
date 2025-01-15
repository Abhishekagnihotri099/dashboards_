# filepath: /C:/Users/digvijay221046/Desktop/Git-AG-DJ/dashboards_/backend/backend_app/management/commands/load_data.py
import csv
import random
from django.core.management.base import BaseCommand
from backend_app.models import dsoutcome, Claims, Parameter
from django.utils.dateparse import parse_datetime
from datetime import datetime

class Command(BaseCommand):
    help = 'Load data from dsoutcome_0.2.csv into the Audit model'
    # Delete previous data

    def parse_date(self, date_str):
        if not date_str or date_str == 'NULL':
            return None
        
        date_formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
            '%d-%m-%Y',
            '%m/%d/%Y',
            '%Y/%m/%d'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        print(f"Could not parse date: {date_str}")
        return None
    def handle(self, *args, **kwargs):
        dsoutcome.objects.all().delete()
        print("All data deleted for DSoutcome")
        csv_file_path = 'backend_app/dsoutcome_0.2.csv'
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            claims = list(Claims.objects.all())
            for row in reader:
                try:
                    claim = Claims.objects.get(claim_id=row['claim_id'])
                except Claims.DoesNotExist:
                    claim = random.choice(claims) if claims else None

                parameter = Parameter.objects.get(parameter_id=row['parameter_id'])

                if not dsoutcome.objects.filter(audit_id=row['audit_id']).exists():
                    dsoutcome.objects.create(
                        audit_id=row['audit_id'],
                        claim=claim,
                        complaint_id=row['complaint_id'] if row['complaint_id'] != 'NULL' else None,
                        policy_id=row['policy_id'] if row['policy_id'] != 'NULL' else None,
                        action_needed_flag=row['action_needed_flag'] if row['action_needed_flag'] != 'NULL' else None,
                        ai_signal=row['ai_signal'] if row['ai_signal'] != 'NULL' else None,
                        assigned_by=row['assigned_by'] if row['assigned_by'] != 'NULL' else None,
                        assigned_date=self.parse_date((row['assigned_date'])) if row['assigned_date'] != 'NULL' else None,
                        assigned_userid=row['assigned_userid'] if row['assigned_userid'] != 'NULL' else None,
                        claim_stage=row['claim_stage'] if row['claim_stage'] != 'NULL' else None,
                        claim_status=row['claim_status'] if row['claim_status'] != 'NULL' else None,
                        close_date=self.parse_date(row['close_date']) if row['close_date'] != 'NULL' else None,
                        comments=row['comments'] if row['comments'] != 'NULL' else None,
                        confidence_score=float(row['confidence_score']) if row['confidence_score'] not in ['NULL', ''] else None,
                        consultant_name=row['consultant_name'] if row['consultant_name'] != 'NULL' else None,
                        created_date=self.parse_date(row['created_date']) if row['created_date'] != 'NULL' else None,
                        current_status=row['current_status'] if row['current_status'] != 'NULL' else None,
                        dsoutcome_key_retrigger=row['dsoutcome_key_retrigger'] if row['dsoutcome_key_retrigger'] != 'NULL' else None,
                        exposure_details=row['exposure_details'] if row['exposure_details'] != 'NULL' else None,
                        exposure_id=row['exposure_id'] if row['exposure_id'] != 'NULL' else None,
                        final_leakage_amount=float(row['final_leakage_amount']) if row['final_leakage_amount'] not in ['NULL', ''] else None,
                        final_signal=row['final_signal'] if row['final_signal'] != 'NULL' else None,
                        indicator_value=row['indicator_value'] if row['indicator_value'] != 'NULL' else None,
                        indicator_name=row['indicator_name'] if row['indicator_name'] != 'NULL' else None,
                        indicator_percentage=float(row['indicator_percentage']) if row['indicator_percentage'] not in ['NULL', ''] else None,
                        is_broker=row['is_broker'] == 'TRUE' if row['is_broker'] != 'NULL' else None,
                        isdeleted=row['isdeleted'] == 'TRUE' if row['isdeleted'] != 'NULL' else None,
                        isvalidated=row['isvalidated'] == 'TRUE' if row['isvalidated'] != 'NULL' else None,
                        leakage_level=row['leakage_level'] if row['leakage_level'] != 'NULL' else None,
                        leakage_type=row['leakage_type'] if row['leakage_type'] != 'NULL' else None,
                        manual_signal=row['manual_signal'] if row['manual_signal'] != 'NULL' else None,
                        manual_leakage_amount=float(row['manual_leakage_amount']) if row['manual_leakage_amount'] not in ['NULL', ''] else None,
                        month_begin=self.parse_date(row['month_begin']) if row['month_begin'] != 'NULL' else None,
                        notification_status=row['notification_status'] if row['notification_status'] != 'NULL' else None,
                        notification_comment=row['notification_comment'] if row['notification_comment'] != 'NULL' else None,
                        parameter=parameter,
                        parameter_name=row['parameter_name'] if row['parameter_name'] != 'NULL' else None,
                        parameter_stage=row['parameter_stage'] if row['parameter_stage'] != 'NULL' else None,
                        payset_id=row['payset_id'] if row['payset_id'] != 'NULL' else None,
                        potential_leakage_amount=float(row['potential_leakage_amount']) if row['potential_leakage_amount'] not in ['NULL', ''] else None,
                        recommended_action=row['recommended_action'] if row['recommended_action'] != 'NULL' else None,
                        reconsider_age=int(float(row['reconsider_age'])) if row['reconsider_age'] not in ['NULL', ''] else None,
                        reconsideration_date=self.parse_date(row['reconsideration_date']) if row['reconsideration_date'] != 'NULL' else None,
                        reconsideration_flag=row['reconsideration_flag'] == 'TRUE' if row['reconsideration_flag'] != 'NULL' else None,
                        response_assigned_supervisor=row['response_assigned_supervisor'] if row['response_assigned_supervisor'] != 'NULL' else None,
                        response_submitted_by=row['response_submitted_by'] if row['response_submitted_by'] != 'NULL' else None,
                        retrigger_required=row['retrigger_required'] == 'TRUE' if row['retrigger_required'] != 'NULL' else None,
                        retrigger_status=row['retrigger_status'] if row['retrigger_status'] != 'NULL' else None,
                        row_age=int(float(row['row_age'])) if row['row_age'] not in ['NULL', ''] else None,
                        signal_close_date=self.parse_date(row['signal_close_date']) if row['signal_close_date'] != 'NULL' else None,
                        signal_id=row['signal_id'] if row['signal_id'] != 'NULL' else None,
                        signal_propensity=float(row['signal_propensity']) if row['signal_propensity'] not in ['NULL', ''] else None,
                        signalfile_reference=row['signalfile_reference'] if row['signalfile_reference'] != 'NULL' else None,
                        team_name=row['team_name'] if row['team_name'] != 'NULL' else None,
                        trigger_age=int(float(row['trigger_age'])) if row['trigger_age'] not in ['NULL', ''] else None,
                        update_screen=row['update_screen'] if row['update_screen'] != 'NULL' else None,
                        use_case=row['use_case'] if row['use_case'] != 'NULL' else None,
                        week_begin=self.parse_date(row['week_begin']) if row['week_begin'] != 'NULL' else None,
                        lob=row['lob'] if row['lob'] != 'NULL' else None
                    )
        self.stdout.write(self.style.SUCCESS('Data loaded successfully'))


