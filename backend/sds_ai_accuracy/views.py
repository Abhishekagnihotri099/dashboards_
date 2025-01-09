from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q, Avg, Count
from backend_app.models import Claims, ClaimAuditable, Parameter, dsoutcome
import pandas as pd
import plotly.graph_objects as go
import json
def filter_data_ai_accuracy(request):
    # Extract query parameters with date ranges
    filters = {
        'ai_monitoring_start_date': request.GET.get('ai_monitoring_start_date'),
        'ai_monitoring_end_date': request.GET.get('ai_monitoring_end_date'),
        'manual_monitoring_start_date': request.GET.get('manual_monitoring_start_date'),
        'manual_monitoring_end_date': request.GET.get('manual_monitoring_end_date'),
        'parameter_name': request.GET.get('parameter_name'),
        'leakage_category': request.GET.get('leakage_category'),
        'line_of_business': request.GET.get('line_of_business'),
        'audited_by': request.GET.get('audited_by'),
        'parameter_score_ai': request.GET.get('parameter_score_ai'),
    }
    print(filters)
    # Build query
    query = Q()
    if filters['parameter_name'] and filters['parameter_name'] != 'All':
        query &= Q(parameter_name=filters['parameter_name'])
    if filters['line_of_business'] and filters['line_of_business'] != 'All':
        query &= Q(claim__lob=filters['line_of_business'])
    if filters['audited_by'] and filters['audited_by'] != 'All':
        query &= Q(claim__response_submitted_by=filters['audited_by'])
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
    # if filters['manual_monitoring_start_date'] and filters['manual_monitoring_end_date']:
    #     query &= Q(parameter_audit_date__range=[
    #         filters['manual_monitoring_start_date'], 
    #         filters['manual_monitoring_end_date']
    #     ])

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
                'parameter_audit_date': audit.parameter_audit_date,
                'parameter_name': audit.parameter_name,
                'leakage_category': audit.claim.dsoutcomes.first().leakage_category if audit.claim.dsoutcomes.exists() else None,
                'accuracy_numerator': audit.accuracy_numerator,
                'accuracy_denominator': audit.accuracy_denominator
            }
            for audit in claim_auditables[start:end]
        ],
        'total_records': claim_auditables.count(),
        'page': page,
        'page_size': page_size,
    }
    print(response_data['total_records'])
    return JsonResponse(response_data)

def generate_yearly_ai_accuracy(claim_audit_df):
    # Convert and extract year
    claim_audit_df['audit_date'] = pd.to_datetime(claim_audit_df['audit_date'])
    claim_audit_df['year'] = claim_audit_df['audit_date'].dt.year
    
    # Calculate yearly accuracy
    yearly_accuracy = claim_audit_df.groupby('year').agg({
        'accuracy_numerator': 'sum',
        'accuracy_denominator': 'sum'
    }).reset_index()
    
    # Calculate accuracy percentage
    yearly_accuracy['ai_accuracy'] = (
        yearly_accuracy['accuracy_numerator'] / 
        yearly_accuracy['accuracy_denominator'] * 100
    ).fillna(0)

    # Create bar chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=yearly_accuracy['year'],
        y=yearly_accuracy['ai_accuracy'],
        name='AI Accuracy %',
        marker_color='royalblue',
        text=yearly_accuracy['ai_accuracy'].round(2),
        textposition='auto'
    ))

    fig.update_layout(
        title='Yearly AI Accuracy Trend',
        xaxis_title='Year',
        yaxis_title='AI Accuracy %',
        yaxis=dict(
            tickformat=',.1f',
            range=[0, 100]
        ),
        showlegend=True,
        height=400
    )
    
    return fig.to_json()

def generate_monthly_parameter_accuracy(claim_audit_df):
    # Convert to datetime
    claim_audit_df['audit_date'] = pd.to_datetime(claim_audit_df['audit_date'])
    
    # Create month column in MMM_YY format and sort chronologically
    claim_audit_df['month'] = claim_audit_df['audit_date'].dt.strftime('%b_%y')
    months_sorted = sorted(claim_audit_df['month'].unique(), 
                         key=lambda x: pd.to_datetime(x, format='%b_%y'), 
                         reverse=True)
    
    # Calculate monthly accuracies
    monthly_param = claim_audit_df.groupby(['parameter_name', 'month']).agg({
        'accuracy_numerator': 'sum',
        'accuracy_denominator': 'sum'
    }).reset_index()
    
    # Calculate accuracy percentage
    monthly_param['accuracy'] = (
        monthly_param['accuracy_numerator'] / 
        monthly_param['accuracy_denominator'] * 100
    ).fillna(0)
    
    # Create pivot table
    pivot_df = pd.pivot_table(
        monthly_param,
        values='accuracy',
        index='parameter_name',
        columns='month',
        fill_value=0
    ).reset_index()
    
    # Calculate overall accuracy
    overall = claim_audit_df.groupby('parameter_name').agg({
        'accuracy_numerator': 'sum',
        'accuracy_denominator': 'sum'
    })
    overall['overall_accuracy'] = (
        overall['accuracy_numerator'] / 
        overall['accuracy_denominator'] * 100
    ).fillna(0)
    
    # Merge overall with pivot
    final_df = pd.merge(
        pivot_df,
        overall['overall_accuracy'].round(2),
        left_on='parameter_name',
        right_index=True
    )
    
    # Reorder columns
    month_cols = [col for col in final_df.columns if col not in ['parameter_name', 'overall_accuracy']]
    final_df = final_df[['parameter_name', 'overall_accuracy'] + month_cols]
    
    # Round all accuracy values
    for col in final_df.columns:
        if col != 'parameter_name':
            final_df[col] = final_df[col].round(2)
            
    return final_df.to_dict('records')

def ai_accuracy_view(request):
    filtered_response = filter_data_ai_accuracy(request)
    filtered_data = filtered_response.content
    claim_audit_data = json.loads(filtered_data)['claim_audit_data']
    claim_audit_df = pd.DataFrame(claim_audit_data)
    
    # Calculate metrics
    claims_monitored_by_ai = len(claim_audit_df['claim_id'].unique())
    
    # Claims monitored manually
    manual_scores = ['Met', 'Not Met', 'NA', 'Not Applicable']
    claims_monitored_manually = len(
        claim_audit_df[claim_audit_df['parameter_score_ai'].isin(manual_scores)]['claim_id'].unique()
    )
    
    # Percentage of claims monitored manually
    percent_manual = (claims_monitored_manually / claims_monitored_by_ai * 100) if claims_monitored_by_ai > 0 else 0
    
    # Overall AI accuracy
    ai_accuracy = (
        claim_audit_df['accuracy_numerator'].sum() / 
        claim_audit_df['accuracy_denominator'].sum() * 100
    ) if claim_audit_df['accuracy_denominator'].sum() > 0 else 0
    
    # Generate charts and tables
    yearly_accuracy_json = generate_yearly_ai_accuracy(claim_audit_df)
    monthly_parameter_accuracy = generate_monthly_parameter_accuracy(claim_audit_df)
    
    return JsonResponse({
        'yearly_accuracy_trend': yearly_accuracy_json,
        'claims_monitored_by_ai': claims_monitored_by_ai,
        'claims_monitored_manually': claims_monitored_manually,
        'percent_claims_monitored_manually': round(percent_manual, 2),
        'ai_accuracy': round(ai_accuracy, 2),
        'monthly_parameter_accuracy': monthly_parameter_accuracy
    })