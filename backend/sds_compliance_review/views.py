from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.db.models import Q, Count, Sum, Case, When, IntegerField, FloatField, F
from backend_app.models import dsoutcome
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import base64

@api_view(['GET'])
def filter_compliance_review(request):
    # Extract query parameters
    filters = {
        'monitoring_date_start': request.GET.get('monitoring_date_start'),
        'monitoring_date_end': request.GET.get('monitoring_date_end'),
        'loss_date_start': request.GET.get('loss_date_start'),
        'loss_date_end': request.GET.get('loss_date_end'),
        'claim_closed_date_start': request.GET.get('claim_closed_date_start'),
        'claim_closed_date_end': request.GET.get('claim_closed_date_end'),
        'line_of_business': request.GET.getlist('line_of_business', []),
        'sub_line_of_business': request.GET.getlist('sub_line_of_business', []),
        'nature_of_loss': request.GET.getlist('nature_of_loss', []),
        'cause_of_loss': request.GET.getlist('cause_of_loss', []),
        'claim_status': request.GET.getlist('claim_status', []),
        'claim_state': request.GET.getlist('claim_state', []),
        'claim_consultant': request.GET.getlist('claim_consultant', []),
        'team': request.GET.getlist('team', []),
        'accurate_signal': request.GET.get('accurate_signal'),
        'brand': request.GET.getlist('brand', []),
        'compliance_category': request.GET.getlist('compliance_category', []),
        'parameter_name': request.GET.get('parameter_name'),
        'signal_status': request.GET.get('signal_status'),
        'manual_review': request.GET.get('manual_review'),
        'signal_reviewed_by': request.GET.get('signal_reviewed_by'),
    }
    print(filters)
    
    # Build query
    query = Q()
    if filters['monitoring_date_start'] and filters['monitoring_date_end']:
        query &= Q(claim__audits__audit_date__date__range=[filters['monitoring_date_start'], filters['monitoring_date_end']])
    if filters['loss_date_start'] and filters['loss_date_end']:
        query &= Q(claim__loss_date__range=[filters['loss_date_start'], filters['loss_date_end']])
    if filters['claim_closed_date_start'] and filters['claim_closed_date_end']:
        query &= Q(claim__close_date__range=[filters['claim_closed_date_start'], filters['claim_closed_date_end']])
    if filters['line_of_business']:
        query &= Q(lob__in=filters['line_of_business'])
    if filters['sub_line_of_business']:
        query &= Q(sub_line_of_business__in=filters['sub_line_of_business'])
    if filters['nature_of_loss']:
        query &= Q(nature_of_loss__in=filters['nature_of_loss'])
    if filters['cause_of_loss']:
        query &= Q(cause_of_loss__in=filters['cause_of_loss'])
    if filters['claim_status']:
        query &= Q(claim_status__in=filters['claim_status'])
    if filters['claim_state']:
        query &= Q(claim_state__in=filters['claim_state'])
    if filters['claim_consultant']:
        query &= Q(claim_consultant__in=filters['claim_consultant'])
    if filters['team']:
        query &= Q(team__in=filters['team'])
    if filters['accurate_signal']:
        query &= Q(accurate_signal=filters['accurate_signal'])
    if filters['brand']:
        query &= Q(brand__in=filters['brand'])
    if filters['compliance_category']:
        query &= Q(compliance_category__in=filters['compliance_category'])
    if filters['parameter_name']:
        query &= Q(parameter_name__icontains=filters['parameter_name'])
    if filters['signal_status']:
        query &= Q(signal_status=filters['signal_status'])
    if filters['manual_review']:
        query &= Q(manual_review=filters['manual_review'])
    if filters['signal_reviewed_by']:
        query &= Q(signal_reviewed_by=filters['signal_reviewed_by'])
    
    # Query database
    signals = dsoutcome.objects.filter(query)
    
    # Calculate metrics
    metrics = signals.aggregate(
        claims_monitored=Count('claim_id'),
        claims_with_compliance_opportunity=Count('claim_id', filter=Q(ai_signal='Yes') & Q(signal_id__in=["S7", "S8", "S9", "S10", "S11"])),
        compliance_opportunity_percentage=Case(
            When(claims_monitored__gt=0, then=F('claims_with_compliance_opportunity') * 100.0 / F('claims_monitored')),
            default=0,
            output_field=FloatField()
        )
    )
    
    # Round off metric values
    rounded_metrics = {key: round(value, 2) if isinstance(value, (int, float)) else value for key, value in metrics.items()}
    
    # Prepare data for table
    table_data = signals.values('parameter__parameter_id').annotate(
        claims_monitored=Count('claim_id'),
        claims_with_compliance_opportunity=Count('claim_id', filter=Q(ai_signal='Yes') & Q(signal_id__in=["S7", "S8", "S9", "S10", "S11"])),
        compliance_opportunity_percentage=Case(
            When(claims_monitored__gt=0, then=F('claims_with_compliance_opportunity') * 100.0 / F('claims_monitored')),
            default=0,
            output_field=FloatField()
        )
    )
    
    # Convert table data to DataFrame for better manipulation
    df_table = pd.DataFrame(list(table_data))
    
    # Generate graphs
    graphs = {}
    
    # 1st Graph: Compliance Opportunities Trend
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(x=df_table['signal_generated_date'], y=df_table['claims_with_compliance_opportunity'], name='Claims with Compliance Opportunity'))
    fig1.add_trace(go.Scatter(x=df_table['signal_generated_date'], y=df_table['compliance_opportunity_percentage'], mode='lines', name='Compliance Opportunity %'))
    fig1.add_trace(go.Scatter(x=df_table['signal_generated_date'], y=df_table['claims_monitored'], mode='lines', name='Claims Monitored'))
    fig1.update_layout(title='Compliance Opportunities Trend', xaxis_title='Signal Generated Date', yaxis_title='Count')
    graphs['compliance_opportunities_trend'] = fig1.to_html(full_html=False)
    
    # 2nd Graph: Compliance Opportunities by Category (Pie Chart)
    df_pie = df_table.groupby('leakage_category').sum().reset_index()
    fig2 = px.pie(df_pie, names='leakage_category', values='claims_with_compliance_opportunity', title='Compliance Opportunities by Category')
    graphs['compliance_opportunities_by_category'] = fig2.to_html(full_html=False)
    
    # 3rd Graph: Compliance Opportunities by Claim Consultant (Treemap)
    df_treemap = df_table.groupby('consultant_name').sum().reset_index()
    fig3 = px.treemap(df_treemap, path=['consultant_name'], values='claims_with_compliance_opportunity', title='Compliance Opportunities by Claim Consultant')
    graphs['compliance_opportunities_by_consultant'] = fig3.to_html(full_html=False)
    
    # 4th Graph: Compliance Opportunities by Parameter (Bar Chart)
    fig4 = px.bar(df_table, x='parameter_name', y='claims_with_compliance_opportunity', title='Compliance Opportunities by Parameter')
    graphs['compliance_opportunities_by_parameter'] = fig4.to_html(full_html=False)
    
    # 5th Graph: Error % by Claim Consultant (Bar Graph)
    fig5 = go.Figure()
    fig5.add_trace(go.Bar(x=df_table['consultant_name'], y=df_table['ai_signal'], name='AI Signal'))
    fig5.add_trace(go.Scatter(x=df_table['consultant_name'], y=df_table['ai_error_final'], mode='lines', name='AI Error Final'))
    fig5.update_layout(title='Error % by Claim Consultant', xaxis_title='Consultant Name', yaxis_title='AI Signal')
    graphs['error_by_consultant'] = fig5.to_html(full_html=False)
    
    # 6th Graph: Claim Opportunity by Compliance Reasons and Category (Ribbon Graph)
    fig6 = px.sunburst(df_table, path=['notification_comment', 'leakage_category'], values='claims_with_compliance_opportunity', title='Claim Opportunity by Compliance Reasons and Category')
    graphs['claim_opportunity_by_compliance_reasons'] = fig6.to_html(full_html=False)
    
    # Return metrics, graphs, and table data as JSON response
    return JsonResponse({
        'metrics': rounded_metrics,
        'graphs': graphs,
        'table_data': df_table.to_dict(orient='records')
    })