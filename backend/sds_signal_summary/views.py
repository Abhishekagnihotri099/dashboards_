from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.db.models import Q, Count, Sum, Case, When, IntegerField, FloatField
from backend_app.models import dsoutcome
import pandas as pd

def filter_signal_summary(request):
    # Extract query parameters
    filters = {
        'signal_generated_start_date': request.GET.get('signal_generated_start_date'),
        'signal_generated_end_date': request.GET.get('signal_generated_end_date'),
        'signal_assigned_start_date': request.GET.get('signal_assigned_start_date'),
        'signal_assigned_end_date': request.GET.get('signal_assigned_end_date'),
        'signal_closed_start_date': request.GET.get('signal_closed_start_date'),
        'signal_closed_end_date': request.GET.get('signal_closed_end_date'),
        'line_of_business': request.GET.getlist('line_of_business', []),
        'parameter_id': request.GET.get('parameter_name'),
    }
    print(filters)
    
    # Build query
    query = Q()
    if filters['signal_generated_start_date'] and filters['signal_generated_end_date']:
        # replace audit date with signal genertaed date
        query &= Q(claim__audits__audit_date__date__range=[
            filters['signal_generated_start_date'], 
            filters['signal_generated_end_date']
        ])
    if filters['signal_assigned_start_date'] and filters['signal_assigned_end_date']:
        # replace audit date with assigned date
        query &= Q(claim__audits__audit_date__date__range=[
            filters['signal_assigned_start_date'], 
            filters['signal_assigned_end_date']
        ])
    if filters['signal_closed_start_date'] and filters['signal_closed_end_date']:
        # replace audit date with closed date
        query &= Q(claim__audits__audit_date__date__range=[
            filters['signal_closed_start_date'], 
            filters['signal_closed_end_date']
        ])
    if filters['line_of_business'] and 'All' not in filters['line_of_business']:
        query &= Q(lob__in=filters['line_of_business'])
    if filters['parameter_id']:
        query &= Q(parameter__stored_pid=filters['parameter_id'])
    
    # Query database
    signals = dsoutcome.objects.filter(query)
    print(signals)
    # Calculate metrics
    metrics = signals.aggregate(
        signals_generated=Count('claim_id', filter=Q(ai_signal='Yes') & ~Q(signal_id='DE') & ~Q(response_submitted_by='Lisa McComb')),
        signals_reviewed=Count('audit_id', filter=Q(ai_signal='Yes') & ~Q(signal_id='DE') & ~Q(response_submitted_by='Lisa McComb') & ~Q(action_needed_flag=None)),
        signals_aligned_with_leakage=Count('audit_id', filter=Q(ai_signal='Yes') & ~Q(signal_id='DE') & ~Q(response_submitted_by='Lisa McComb') & Q(action_needed_flag__in=['Yes', 'No']) & ~Q(final_leakage_amount=0)),
        signals_aligned_without_leakage=Count('audit_id', filter=Q(ai_signal='Yes') & ~Q(signal_id='DE') & Q(action_needed_flag__in=['Yes', 'No']) & Q(final_leakage_amount=0)),
        signals_not_aligned=Count('audit_id', filter=Q(ai_signal='Yes') & ~Q(signal_id='DE') & Q(action_needed_flag='Incorrect Signal')),
        signals_awaiting_action=Count('audit_id', filter=Q(ai_signal='Yes') & ~Q(signal_id='DE') & ~Q(response_assigned_supervisor=None) & Q(signal_close_date=None)),
        signals_not_actioned_on_time=Count('audit_id', filter=Q(ai_signal='Yes') & ~Q(signal_id='DE') & Q(notification_status='Actioned') & Q(action_needed_flag=None) & ~Q(response_assigned_supervisor=None)),
        leakage_identified_by_ai=Sum('potential_leakage_amount', filter=Q(ai_signal='Yes') & ~Q(signal_id='DE') & ~Q(response_submitted_by='Lisa McComb')),
        leakage_reviewed=Sum('potential_leakage_amount', filter=Q(ai_signal='Yes') & ~Q(signal_id='DE') & ~Q(response_submitted_by='Lisa McComb') & ~Q(action_needed_flag=None) & Q(notification_status='Actioned')),
        leakage_on_aligned_signal=Sum('potential_leakage_amount', filter=Q(ai_signal='Yes') & ~Q(signal_id='DE') & ~Q(response_submitted_by='Lisa McComb') & Q(action_needed_flag__in=['Yes', 'No']) & Q(notification_status='Actioned') & Q(potential_leakage_amount__gt=0)),
        leakage_validated=Sum('final_leakage_amount', filter=Q(ai_signal='Yes') & ~Q(signal_id='DE') & Q(notification_status='Actioned') & Q(action_needed_flag__in=['Yes', 'No']) & ~Q(response_submitted_by='Lisa McComb')),
        leakage_saved=Sum('final_leakage_amount', filter=Q(ai_signal='Yes') & ~Q(signal_id='DE') & Q(notification_status='Actioned') & Q(action_needed_flag='Yes') & ~Q(response_submitted_by='Lisa McComb'))
    )

    rounded_metrics = {key: round(value, 2) if isinstance(value, (int, float)) else value for key, value in metrics.items()}
    
    # Prepare data for table
    table_data = signals.values('parameter__parameter_id').annotate(
        signals_generated=Count('audit_id', filter=Q(ai_signal='Yes') & ~Q(signal_id='DE') & ~Q(response_submitted_by='Lisa McComb')),
        signals_reviewed=Count('audit_id', filter=Q(ai_signal='Yes') & ~Q(signal_id='DE') & ~Q(response_submitted_by='Lisa McComb') & ~Q(action_needed_flag=None)),
        signals_aligned_with_leakage=Count('audit_id', filter=Q(ai_signal='Yes') & ~Q(signal_id='DE') & ~Q(response_submitted_by='Lisa McComb') & Q(action_needed_flag__in=['Yes', 'No']) & ~Q(final_leakage_amount=0)),
        signals_aligned_without_leakage=Count('audit_id', filter=Q(ai_signal='Yes') & ~Q(signal_id='DE') & Q(action_needed_flag__in=['Yes', 'No']) & Q(final_leakage_amount=0)),
        signals_not_aligned=Count('audit_id', filter=Q(ai_signal='Yes') & ~Q(signal_id='DE') & Q(action_needed_flag='Incorrect Signal')),
        signals_awaiting_action=Count('audit_id', filter=Q(ai_signal='Yes') & ~Q(signal_id='DE') & ~Q(response_assigned_supervisor=None) & Q(signal_close_date=None)),
        signals_not_actioned_on_time=Count('audit_id', filter=Q(ai_signal='Yes') & ~Q(signal_id='DE') & Q(notification_status='Actioned') & Q(action_needed_flag=None) & ~Q(response_assigned_supervisor=None)),
        leakage_identified_by_ai=Sum('potential_leakage_amount', filter=Q(ai_signal='Yes') & ~Q(signal_id='DE') & ~Q(response_submitted_by='Lisa McComb')),
        leakage_reviewed=Sum('potential_leakage_amount', filter=Q(ai_signal='Yes') & ~Q(signal_id='DE') & ~Q(response_submitted_by='Lisa McComb') & ~Q(action_needed_flag=None) & Q(notification_status='Actioned')),
        leakage_on_aligned_signal=Sum('potential_leakage_amount', filter=Q(ai_signal='Yes') & ~Q(signal_id='DE') & ~Q(response_submitted_by='Lisa McComb') & Q(action_needed_flag__in=['Yes', 'No']) & Q(notification_status='Actioned') & Q(potential_leakage_amount__gt=0)),
        leakage_validated=Sum('final_leakage_amount', filter=Q(ai_signal='Yes') & ~Q(signal_id='DE') & Q(notification_status='Actioned') & Q(action_needed_flag__in=['Yes', 'No']) & ~Q(response_submitted_by='Lisa McComb')),
        leakage_saved=Sum('final_leakage_amount', filter=Q(ai_signal='Yes') & ~Q(signal_id='DE') & Q(notification_status='Actioned') & Q(action_needed_flag='Yes') & ~Q(response_submitted_by='Lisa McComb'))
    )
    
    # Convert table data to DataFrame for better manipulation
    df_table = pd.DataFrame(list(table_data))
    
    # Return metrics and table data as JSON response
    return JsonResponse({
        'metrics': rounded_metrics,
        'table_data': df_table.to_dict(orient='records')
    })