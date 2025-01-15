from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from backend_app.models import Claims, ClaimAuditable, Parameter, dsoutcome
import pandas as pd
import json
import plotly.graph_objects as go
def filter_data_ai_coverage(request):
    # Extract query parameters
    filters = {
        'ai_monitoring_start_date': request.GET.get('ai_monitoring_start_date'),
        'ai_monitoring_end_date': request.GET.get('ai_monitoring_end_date'),
        'parameter_name': request.GET.get('parameter_name'),
        'leakage_category': request.GET.get('leakage_category'),
        'line_of_business': request.GET.get('line_of_business'),
        'parameter_score_ai': request.GET.get('parameter_score_ai'),
    }

    # Build query
    query = Q()
    if filters['parameter_name'] and filters['parameter_name'] != 'All':
        query &= Q(parameter_name=filters['parameter_name'])
    if filters['line_of_business'] and filters['line_of_business'] != 'All':
        query &= Q(claim__lob=filters['line_of_business'])
    if filters['parameter_score_ai'] and filters['parameter_score_ai'] != 'All':
        query &= Q(parameter_score_ai=filters['parameter_score_ai'])
    if filters['leakage_category'] and filters['leakage_category'] != 'All':
        query &= Q(claim__dsoutcomes__leakage_category=filters['leakage_category'])

    # Date range filters
    if filters['ai_monitoring_start_date'] and filters['ai_monitoring_end_date']:
        query &= Q(audit_date__range=[
            filters['ai_monitoring_start_date'], 
            filters['ai_monitoring_end_date']
        ])

    # Query database with optimized joins
    claim_auditables = ClaimAuditable.objects.select_related(
        'claim',
        'parameter'
    ).prefetch_related(
        'claim__dsoutcomes'
    ).filter(query)

    # Paginate
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 1000))
    start = (page - 1) * page_size
    end = start + page_size

    response_data = {
        'claim_audit_data': [
            {
                'claim_id': audit.claim.claim_id,
                'audit_date': audit.audit_date,
                'parameter_score_ai': audit.parameter_score_ai,
                'parameter_name': audit.parameter_name,
                'leakage_category': audit.claim.dsoutcomes.first().leakage_category if audit.claim.dsoutcomes.exists() else None,
                'line_of_business': audit.claim.lob,
                'due_date' : audit.due_date,
                'pid' : audit.parameter.parameter_id
            }
            for audit in claim_auditables[start:end]
        ],
        'total_records': claim_auditables.count(),
        'page': page,
        'page_size': page_size,
    }

    return JsonResponse(response_data)

def generate_ai_coverage_metrics(claim_audit_df):
    # Total claims
    total_claims = len(claim_audit_df['claim_id'].unique())
    
    # Successfully monitored claims
    valid_ai_scores = ['Met', 'Not Met', 'NA']
    claims_monitored = len(
        claim_audit_df[
            (claim_audit_df['parameter_score_ai'].isin(valid_ai_scores)) & 
            (claim_audit_df['due_date'].notna())
        ]['claim_id'].unique()
    )
    
    # Calculate coverage percentage
    coverage_percentage = (claims_monitored / total_claims * 100) if total_claims > 0 else 0
    
    return {
        'total_claims': total_claims,
        'claims_monitored_successfully': claims_monitored,
        'coverage_percentage': round(coverage_percentage, 2)
    }

def generate_parameter_coverage_table(claim_audit_df):
    # Convert to datetime and create month column
    claim_audit_df['audit_date'] = pd.to_datetime(claim_audit_df['audit_date'])
    claim_audit_df['month'] = claim_audit_df['audit_date'].dt.strftime('%b-%y')
    
    # Calculate opportunities by parameter
    opportunities = claim_audit_df[claim_audit_df['due_date'].notna()].groupby(
        'parameter_name'
    )['pid'].count().reset_index(name='opportunities')
    
    # Calculate overall coverage by parameter
    overall_coverage = claim_audit_df.groupby('parameter_name').apply(
        lambda x: len(x[x['due_date'].notna()]['claim_id'].unique()) / 
                 len(x['claim_id'].unique()) * 100 if len(x['claim_id'].unique()) > 0 else 0
    ).reset_index(name='overall_coverage')
    
    # Calculate monthly coverage by parameter
    monthly_coverage = claim_audit_df.groupby(['parameter_name', 'month']).apply(
        lambda x: len(x[x['due_date'].notna()]['claim_id'].unique()) / 
                 len(x['claim_id'].unique()) * 100 if len(x['claim_id'].unique()) > 0 else 0
    ).reset_index(name='coverage')
    
    # Create pivot table for monthly coverage
    pivot_df = monthly_coverage.pivot(
        index='parameter_name',
        columns='month',
        values='coverage'
    ).reset_index()
    
    # Merge all metrics
    final_df = opportunities.merge(
        overall_coverage, 
        on='parameter_name'
    ).merge(
        pivot_df,
        on='parameter_name'
    )
    
    # Sort months in reverse chronological order
    month_cols = [col for col in final_df.columns if '-' in str(col)]
    sorted_month_cols = sorted(
        month_cols,
        key=lambda x: pd.to_datetime(x, format='%b-%y'),
        reverse=True
    )
    
    # Reorder columns
    final_cols = ['parameter_name', 'opportunities', 'overall_coverage'] + sorted_month_cols
    final_df = final_df[final_cols]
    
    # Round percentage columns
    for col in final_df.columns:
        if col not in ['parameter_name', 'opportunities']:
            final_df[col] = final_df[col].round(2)
            
    return final_df.to_dict('records')



def generate_ai_coverage_graph(claim_audit_df):
    # Group by audit date
    daily_metrics = claim_audit_df.groupby('audit_date').apply(
        lambda x: pd.Series({
            'total_claims': len(x['claim_id'].unique()),
            'claims_monitored': len(x[
                (x['parameter_score_ai'].isin(['Met', 'Not Met', 'NA'])) & 
                (x['due_date'].notna())
            ]['claim_id'].unique())
        })
    ).reset_index()
    
    # Calculate daily coverage percentage
    daily_metrics['coverage_percentage'] = (
        daily_metrics['claims_monitored'] / daily_metrics['total_claims'] * 100
    ).fillna(0)
    
    # Create bar chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=daily_metrics['audit_date'],
        y=daily_metrics['coverage_percentage'],
        name='AI Coverage %',
        text=daily_metrics['coverage_percentage'].round(2),
        textposition='auto'
    ))
    
    fig.update_layout(
        title='AI Coverage Trend',
        xaxis_title='Audit Date',
        yaxis_title='Coverage %',
        yaxis=dict(range=[0, 100])
    )
    
    return fig.to_json()

def ai_coverage_view(request):
    filtered_response = filter_data_ai_coverage(request)
    filtered_data = json.loads(filtered_response.content)
    claim_audit_df = pd.DataFrame(filtered_data['claim_audit_data'])
    
    metrics = generate_ai_coverage_metrics(claim_audit_df)
    coverage_graph = generate_ai_coverage_graph(claim_audit_df)
    parameter_coverage = generate_parameter_coverage_table(claim_audit_df)
    
    return JsonResponse({
        'metrics': metrics,
        'coverage_graph': coverage_graph,
        'parameter_coverage': parameter_coverage
    })