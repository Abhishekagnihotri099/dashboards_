from django.db import models
from django.db.models import Max, Sum, F, Value, CharField, Case, When, Count, Q, ExpressionWrapper, DecimalField
from django.db.models.functions import Coalesce
from django.db import models
from django.db.models import Max, F
from django.db.models.functions import Coalesce
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.dateparse import parse_date
from datetime import datetime, timedelta


class Claims(models.Model):
    claim_id = models.CharField(max_length=100, primary_key=True)
    remaining_reserve = models.FloatField(null=True)
    paid_amount = models.FloatField(null=True)
    total_recovery = models.FloatField(null=True)
    policy_id = models.CharField(max_length=100, null=True)
    location_state = models.CharField(max_length=100, null=True)
    audit_date = models.DateTimeField(null=True)
    close_date = models.DateTimeField(null=True)
    claim_status = models.CharField(max_length=100, null=True)
    claim_owner_first_name = models.CharField(max_length=100, null=True)
    claim_owner_last_name = models.CharField(max_length=100, null=True)
    general_nature_of_loss = models.CharField(max_length=100, null=True)
    loss_date = models.DateTimeField(null=True)
    loss_claim_cause = models.CharField(max_length=100, null=True)
    lob = models.ForeignKey('LOB', on_delete=models.CASCADE, null=True)
    
    class Meta:
        db_table = 'claims'

    def __str__(self):
        return self.claim_id


class ClaimAuditable(models.Model):
    # Foreign key automatically creates many-to-one relationship
    claim = models.ForeignKey(
        Claims,
        on_delete=models.CASCADE,
        db_index=True,
        related_name='audits'  # Allows Claims.audits.all()
    )
    # parameter_id = models.CharField(max_length=20)
    parameter = models.ForeignKey('Parameter', on_delete=models.CASCADE)
    parameter_score = models.CharField(max_length=20, null=True)
    parameter_score_ai = models.CharField(max_length=20, null=True)
    audit_date = models.DateTimeField(null=True)
    parameter_name = models.CharField(max_length=100, null=True)
    due_date = models.DateTimeField(null=True)
    final_audit_status = models.CharField(max_length=100, null=True)
    parameter_audit_date = models.DateTimeField(null=True)
    lob = models.CharField(max_length=100, null=True)
    final_lob = models.CharField(max_length=100, null=True)
    parameter_comments = models.TextField(null=True)
    MET = models.IntegerField(null=True)
    TOTAL = models.IntegerField(null=True)
    stored_file_review_score = models.FloatField(null=True)

    @property
    def file_review_score(self):
        if self.TOTAL and self.TOTAL != 0:
            return self.MET / self.TOTAL
        return None
    

    @property
    def total(self):
        if self.parameter_score_ai in ["Met", "Not Met"]:
            return 1
        return 0

    @property
    def met(self):
        if self.parameter_score_ai == "Met":
            return 1
        return 0

    @property
    def accuracy_denominator(self):
        """Calculate accuracy denominator based on parameter score"""
        valid_scores = ["Met", "Not Met", "Not Applicable", "NA"]
        return 1 if self.parameter_score_ai in valid_scores else 0

    @property
    def accuracy_numerator(self):
        """Calculate accuracy numerator based on parameter scores"""
        valid_scores = ["Met", "Not Met", "Not Applicable"]
        valid_ai_scores = ["Met", "Not Met", "NA", "Not Applicable"]
        
        # Check if parameter score is valid
        if self.parameter_score_ai not in valid_ai_scores:
            return 0
            
        return 1

    class Meta:
        db_table = 'claim_auditable'

@receiver(pre_save, sender=ClaimAuditable)
def calculate_and_store_values(sender, instance, **kwargs):
    """Calculate and store values before saving"""
    instance.MET = instance.met
    instance.TOTAL = instance.total
    instance.stored_file_review_score = instance.file_review_score



class Parameter(models.Model):
    parameter_id = models.CharField(max_length=100, primary_key=True)
    operationalised_flag = models.CharField(max_length=10, null=True)
    operationalised_status = models.CharField(max_length=100, null=True)
    other_subparameter_id = models.CharField(max_length=100, null=True)
    subtype_name = models.CharField(max_length=100, null=True)
    type_code = models.CharField(max_length=100, null=True)
    type_end_date = models.DateTimeField(null=True)
    type_name = models.CharField(max_length=100, null=True)
    type_start_date = models.DateTimeField(null=True)
    type_status = models.CharField(max_length=100, null=True)
    type_value = models.CharField(max_length=100, null=True)
    compliance_flag = models.CharField(max_length=10, null=True)
    component_of_claim = models.CharField(max_length=100, null=True)
    customer_experience_flag = models.CharField(max_length=10, null=True)
    data_integrity_flag = models.CharField(max_length=10, null=True)
    leakage_flag = models.CharField(max_length=10, null=True)
    indicator_name = models.CharField(max_length=255, null=True)
    line_of_business = models.CharField(max_length=255, null=True)
    parameter_end_date = models.DateTimeField(null=True)
    parameter_no = models.IntegerField(null=True)
    parameter_stage = models.CharField(max_length=100, null=True)
    parameter_start_date = models.DateTimeField(null=True)
    parameter_status = models.CharField(max_length=100, null=True)
    parameter_type = models.CharField(max_length=100, null=True)
    parameter_weightage = models.IntegerField(null=True)
    phase_name = models.CharField(max_length=100, null=True)
    policy_review_flag = models.CharField(max_length=10, null=True)
    question = models.TextField(null=True)
    sampling_methodology = models.CharField(max_length=100, null=True)
    signal_id = models.CharField(max_length=100, null=True)
    signal_level = models.CharField(max_length=100, null=True)
    source_system = models.CharField(max_length=100, null=True)
    triggers = models.CharField(max_length=100, null=True)
    unit_of_measurement = models.CharField(max_length=100, null=True)
    subparameter_description = models.TextField(null=True)
    subparameter_id = models.CharField(max_length=100, null=True)
    stored_pid = models.CharField(max_length=100, null=True)

    @property
    def pid(self):
        return f"{self.parameter_id} - {self.question}"

    def __str__(self):
        return self.parameter_id
@receiver(pre_save, sender=Parameter)
def calculate_and_store_values(sender, instance, **kwargs):
    """Calculate and store values before saving"""
    instance.stored_pid = instance.pid
    
class dsoutcome(models.Model):
    audit_id = models.CharField(max_length=100, primary_key=True)
    claim = models.ForeignKey(Claims, on_delete=models.CASCADE, related_name='dsoutcomes')
    complaint_id = models.CharField(max_length=100, null=True)
    policy_id = models.CharField(max_length=100, null=True)
    action_needed_flag = models.CharField(max_length=10, null=True)
    ai_signal = models.CharField(max_length=100, null=True)
    assigned_by = models.CharField(max_length=100, null=True)
    assigned_date = models.DateTimeField(null=True)
    assigned_userid = models.CharField(max_length=100, null=True)
    claim_stage = models.CharField(max_length=100, null=True)
    claim_status = models.CharField(max_length=100, null=True)
    close_date = models.DateTimeField(null=True)
    comments = models.TextField(null=True)
    confidence_score = models.FloatField(null=True)
    consultant_name = models.CharField(max_length=100, null=True)
    created_date = models.DateTimeField(null=True)
    current_status = models.CharField(max_length=100, null=True)
    dsoutcome_key_retrigger = models.CharField(max_length=100, null=True)
    exposure_details = models.TextField(null=True)
    exposure_id = models.CharField(max_length=100, null=True)
    final_leakage_amount = models.FloatField(null=True)
    final_signal = models.CharField(max_length=100, null=True)
    indicator_value = models.CharField(max_length=100, null=True)
    indicator_name = models.CharField(max_length=255, null=True)
    indicator_percentage = models.FloatField(null=True)
    is_broker = models.BooleanField(null=True)
    isdeleted = models.BooleanField(null=True)
    isvalidated = models.BooleanField(null=True)
    leakage_level = models.CharField(max_length=100, null=True)
    leakage_type = models.CharField(max_length=100, null=True)
    manual_signal = models.CharField(max_length=100, null=True)
    manual_leakage_amount = models.FloatField(null=True)
    month_begin = models.DateTimeField(null=True)
    notification_status = models.CharField(max_length=100, null=True)
    notification_comment = models.TextField(null=True)
    parameter = models.ForeignKey(Parameter, on_delete=models.CASCADE)
    parameter_name = models.CharField(max_length=100, null=True)
    parameter_stage = models.CharField(max_length=100, null=True)
    payset_id = models.CharField(max_length=100, null=True)
    potential_leakage_amount = models.FloatField(null=True)
    recommended_action = models.TextField(null=True)
    reconsider_age = models.IntegerField(null=True)
    reconsideration_date = models.DateTimeField(null=True)
    reconsideration_flag = models.BooleanField(null=True)
    response_assigned_supervisor = models.CharField(max_length=100, null=True)
    response_submitted_by = models.CharField(max_length=100, null=True)
    retrigger_required = models.BooleanField(null=True)
    retrigger_status = models.CharField(max_length=100, null=True)
    row_age = models.IntegerField(null=True)
    signal_close_date = models.DateTimeField(null=True)
    signal_id = models.CharField(max_length=100, null=True)
    signal_propensity = models.FloatField(null=True)
    signalfile_reference = models.CharField(max_length=100, null=True)
    team_name = models.CharField(max_length=100, null=True)
    trigger_age = models.IntegerField(null=True)
    update_screen = models.CharField(max_length=100, null=True)
    use_case = models.CharField(max_length=100, null=True)
    week_begin = models.DateTimeField(null=True)
    lob = models.CharField(max_length=100, null=True)
    # finalized_leakage_amount = models.FloatField(null=True, blank=True)
    stored_ds_paid_remaining = models.FloatField(null=True, blank=True)
    stored_final_leakage = models.FloatField(null=True, blank=True) 
    stored_leakage_rate = models.FloatField(null=True, blank=True)
    stored_exclusions = models.IntegerField(null=True, blank=True)
    stored_leakage_rate_max = models.FloatField(null=True, blank=True)
    stored_leakage_rate_final = models.FloatField(null=True, blank=True)
    stored_leakage_rate_new =  models.FloatField(null=True, blank=True)
    stored_matchornot = models.CharField(max_length=100, null=True, blank=True)
    stored_opp_identified_compliance_review = models.IntegerField(null=True, blank=True)
    stored_opp_identified_compliance_review_ratio = models.FloatField(null=True, blank=True)
    stored_accurate_signal = models.CharField(max_length=100, null=True, blank=True)
    stored_signal_status = models.CharField(max_length=100, null=True, blank=True)
    stored_manual_review = models.CharField(max_length=100, null=True, blank=True)
    stored_no_ai = models.IntegerField(null=True, blank=True)
    stored_no_ai_plus_yes_ai = models.IntegerField(null=True, blank=True)
    stored_ai_error_final = models.FloatField(null=True, blank=True)
    stored_duplicate = models.CharField(max_length=100, null=True, blank=True)
    stored_is_it_a_potential_leakage = models.CharField(max_length=100, null=True, blank=True)
    stored_reported_as_leakage = models.CharField(max_length=100, null=True, blank=True)
    stored_sequence_column = models.IntegerField(null=True, blank=True)
    stored_signal_close_date2 = models.DateTimeField(null=True, blank=True)
    stored_exclusions = models.IntegerField(null=True, blank=True)

    @property
    def MatchinorNot(self):
        if (self.parameter.operationalised_status == "YES" and
            self.signal_close_date and
            self.parameter.parameter_start_date and
            self.parameter.parameter_end_date and
            self.signal_close_date >= self.parameter.parameter_start_date and
            self.signal_close_date <= self.parameter.parameter_end_date):
            return "Yes"
        return "No"
    
    @property
    def ds_paid_remaining(self):
        if self.stored_ds_paid_remaining is not None:
            return self.stored_ds_paid_remaining
        X = self.claim.paid_amount or 0
        Y = self.claim.remaining_reserve or 0
        Z = self.claim.total_recovery or 0
        d = (X or 0) + (Y or 0) - (Z or 0)
        return d
   
    @property
    def get_final_leakage(self):
        if self.stored_final_leakage is not None:
            return self.stored_final_leakage
        if self.leakage_level == "No Leakage":
            return 0
        if self.manual_leakage_amount is None or self.manual_leakage_amount == 0.0:
            return self.potential_leakage_amount or 0
        return self.manual_leakage_amount

    @property 
    def leakage_rate_max_sub_measure(self):
        if self.stored_leakage_rate is not None:
            return self.stored_leakage_rate
        parameter_id = self.parameter.parameter_id
        related_outcomes = dsoutcome.objects.filter(
            parameter_id=parameter_id
        )
        max_leakage = related_outcomes.values('claim_id').annotate(
            max_amount=Coalesce(Max(F('stored_final_leakage')), 0.0)
        )
        return sum(item['max_amount'] for item in max_leakage)
    
    @property
    def exclusions(self):
        if self.ai_signal == "No":
            return 0
        if self.use_case == "AI Exception":
            return 0
        if self.final_leakage_amount <= 0:
            return 0
        return 1
    
    @property
    def leakage_rate_max(self):
        return self.leakage_rate_max_sub_measure if self.exclusions == 1 else 0
    
    @property
    def leakage_rate_final(self):
        return min(self.leakage_rate_max, self.ds_paid_remaining)

    @property
    def leakage_rate_new(self):
        if self.ds_paid_remaining == 0:
            return 0
        return self.leakage_rate_final / self.ds_paid_remaining

    @property
    def leakage_category(self):
        parameter_categories = {
            'GICOP': ['CP1', 'CP2', 'CP3', 'CP4', 'CP5', 'CP6', 'CP7', 'CP8', 'CP9', 'CP10', 
                     'CP12', 'CP13', 'CP14', 'CP15', 'CP16', 'CP17', 'CP20', 'CP21', 'CP22'],
            'RG271': ['CP23', 'CP24', 'CP25', 'CP26', 'CP27', 'CP28', 'CP29', 'CP30'],
            'Privacy': ['CP31', 'CP32', 'CP33', 'CP35'],
            'PCI': ['CP36'],
            'Vulnerable Customer': ['CP37'],
            'CaaFS': ['CP43', 'CP44', 'CP45', 'CP46', 'CP47', 'CP48'],
            'Policy': ['1', '2', '3', '4', '5'],
            'Coverage': ['6', '7', '8'],
            'Settlement': ['9', '10', '11', '12', '13', '14', '22', '23', '24'],
            'Excess': ['15', '16', '17', '18'],
            'Recoveries': ['19', '20', '21', '25'],
            'Validation': ['26', '27', '28', '29', '30'],
            'Assessment/Procurement': ['31', '32', '33', '34', '35', '36']
        }

        parameter_id = self.parameter_id if hasattr(self, 'parameter_id') else None
        
        if parameter_id:
            for category, param_list in parameter_categories.items():
                if parameter_id in param_list:
                    return category
        return None
    
    @property
    def opp_identified_compliance_review(self):
        return dsoutcome.objects.filter(
            ai_signal="Yes",
            signal_id__in=["S7", "S8", "S9", "S10", "S11"]
        ).values('claim_id').distinct().count()

    @property
    def opp_identified_compliance_review_ratio(self):
        total_claims = dsoutcome.objects.values('claim_id').distinct().count()
        if total_claims == 0:
            return 0
        return self.opp_identified_compliance_review / total_claims
    
    @property
    def accurate_signal(self):
        return "No" if self.action_needed_flag == "Incorrect Signal" else "Yes"

    @property
    def signal_status(self):
        if self.notification_status in ["Action Pending", "New"]:
            return "Open"
        elif self.notification_status == "Actioned":
            return "Closed"
        else:
            return "Pending"

    @property
    def manual_review(self):
        return "No" if self.action_needed_flag is None else "Yes"

    @property
    def no_ai(self):
        return dsoutcome.objects.filter(ai_signal="No").count()

    @property
    def no_ai_plus_yes_ai(self):
        return self.no_ai + dsoutcome.objects.filter(ai_signal="Yes").count()

    @property
    def ai_error_final(self):
        total_ai = self.stored_no_ai_plus_yes_ai
        if total_ai == 0:
            return 0
        return self.stored_no_ai / total_ai
    
    @property
    def duplicate(self):
        return f"{self.claim_id.strip()}{self.parameter_id.strip()}{self.payset_id.strip()}{self.exposure_id.strip()}"
    
    @property
    def exclusions(self):
        if self.ai_signal == "No":
            return 0
        if self.use_case == "AI Exception":
            return 0
        if self.stored_final_leakage <= 0:
            return 0
        return 1

    @property
    def is_it_a_potential_leakage(self):
        return "Yes" if self.stored_exclusions == 1 else "No"
    
    @property
    def sequence_column(self):
        if self.exclusions == 0:
            return 0
        related_outcomes = dsoutcome.objects.filter(
            stored_duplicate=self.stored_duplicate
        ).order_by('-claim__audits__audit_date')
        for index, outcome in enumerate(related_outcomes, start=1):
            if outcome == self:
                return index
        return 0

    @property
    def reported_as_leakage(self):
        return "Yes" if self.stored_sequence_column == 1 else "No"

    @property
    def signal_close_date_(self):
        if self.signal_close_date and self.signal_close_date < datetime.date(2023, 1, 1):
            return self.signal_generated_date + datetime.timedelta(days=3)
        return self.signal_close_date


    def __str__(self):
        return self.audit_id

@receiver(pre_save, sender=dsoutcome)
def calculate_and_store_values(sender, instance, **kwargs):
    """Calculate and store values before saving"""
    instance.stored_ds_paid_remaining = instance.ds_paid_remaining
    instance.stored_final_leakage = instance.get_final_leakage
    instance.stored_leakage_rate = instance.leakage_rate_max_sub_measure
    instance.stored_exclusions = instance.exclusions
    instance.stored_leakage_rate_max = instance.leakage_rate_max
    instance.stored_leakage_rate_final = instance.leakage_rate_final
    instance.stored_leakage_rate_new = instance.leakage_rate_new
    instance.stored_matchornot = instance.MatchinorNot
    instance.stored_opp_identified_compliance_review = instance.opp_identified_compliance_review
    instance.stored_opp_identified_compliance_review_ratio = instance.opp_identified_compliance_review_ratio
    instance.stored_accurate_signal = instance.accurate_signal
    instance.stored_signal_status = instance.signal_status
    instance.stored_manual_review = instance.manual_review
    instance.stored_no_ai = instance.no_ai
    instance.stored_no_ai_plus_yes_ai = instance.no_ai_plus_yes_ai
    instance.stored_ai_error_final = instance.ai_error_final
    instance.stored_duplicate = instance.duplicate
    instance.stored_is_it_a_potential_leakage = instance.is_it_a_potential_leakage
    instance.stored_reported_as_leakage = instance.reported_as_leakage
    instance.stored_sequence_column = instance.sequence_column
    instance.stored_signal_close_date2 = instance.signal_close_date_
    instance.stored_exclusions = instance.exclusions

    

    
class LOB(models.Model):
    lob = models.CharField(max_length=100, primary_key=True)
    line_of_business = models.CharField(max_length=100)

    class Meta:
        db_table = 'lob'

    def __str__(self):
        return self.lob
    

class policy(models.Model):
    policy_id = models.CharField(max_length=100)
    distribution_channel = models.CharField(max_length=10)

    class Meta:
        db_table = 'policy'

    def __str__(self):
        return self.policy_id
    

class ClaimNotes(models.Model):
    claim = models.ForeignKey(Claims, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
    group_name = models.CharField(max_length=100)
    update_date = models.DateTimeField()

    class Meta:
        db_table = 'claim_notes'

    def __str__(self):
        return self.claim.claim_id
