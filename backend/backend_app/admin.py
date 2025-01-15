from django.contrib import admin

# Register your models here.
from .models import Claims, ClaimAuditable , Parameter , dsoutcome , LOB , policy , ClaimNotes


class ClaimAuditableAdmin(admin.ModelAdmin):
    list_display = ('claim','parameter_score_ai','total', 'met' , 'accuracy_denominator' , 'accuracy_numerator', 'MET', "TOTAL", 'stored_file_review_score', 'audit_date')

class dsoutcomeAdmin(admin.ModelAdmin):
    list_display = ('parameter_id','leakage_category', 'stored_ds_paid_remaining', 'stored_final_leakage', 'stored_leakage_rate', 'stored_exclusions', 'stored_leakage_rate_max', 'stored_leakage_rate_final', 'stored_leakage_rate_new', 'stored_matchornot', 'created_date', 'stored_ai_error_final')

class ParameterAdmin(admin.ModelAdmin):
    list_display = (
    'parameter_id', 'operationalised_flag', 'operationalised_status', 
    'other_subparameter_id', 'subtype_name', 'type_code', 
    'type_end_date', 'type_name', 'type_start_date', 'type_status', 
    'type_value', 'compliance_flag', 'component_of_claim', 
    'customer_experience_flag', 'data_integrity_flag', 'leakage_flag', 
    'indicator_name', 'line_of_business', 'parameter_end_date', 
    'parameter_no', 'parameter_stage', 'parameter_start_date', 
    'parameter_status', 'parameter_type', 'parameter_weightage', 
    'phase_name', 'policy_review_flag', 'question', 'sampling_methodology', 
    'signal_id', 'signal_level', 'source_system', 'triggers', 
    'unit_of_measurement', 'subparameter_description', 'subparameter_id',
    'stored_pid'
    )


admin.site.register(Claims)

admin.site.register(ClaimAuditable , ClaimAuditableAdmin)

admin.site.register(Parameter, ParameterAdmin)

admin.site.register(dsoutcome, dsoutcomeAdmin)

admin.site.register(LOB)

admin.site.register(policy)

admin.site.register(ClaimNotes)