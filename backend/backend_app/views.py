# filepath: /C:/Users/digvijay221046/Desktop/Git-AG-DJ/dashboards_/backend/backend_app/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from .models import Claims, ClaimAuditable, Parameter , dsoutcome
import pandas as pd
import plotly.graph_objects as go

#Complex chart - 1 Doubtful

def calculate_error_metrics(df, days=None):
    """Calculate error metrics for given timeframe"""
    if days:
        max_date = df['audit_date'].max()
        df = df[df['audit_date'] >= (max_date - pd.Timedelta(days=days))]
    
    error_met = len(df[df['parameter_score_ai'] == 'Met'])
    error_not_met = len(df[df['parameter_score_ai'] == 'Not Met'])
    total_errors = error_met + error_not_met
    error_percentage = (error_met / total_errors * 100) if total_errors > 0 else 0
    
    return total_errors, error_percentage

def generate_consultant_error_chart(claim_audit_df):
    consultant_metrics = []
    
    for consultant in claim_audit_df['consultant_name'].unique():
        consultant_df = claim_audit_df[claim_audit_df['consultant_name'] == consultant]
        
        # Calculate metrics for different periods
        total_7d, pct_7d = calculate_error_metrics(consultant_df, 7)
        total_30d, pct_30d = calculate_error_metrics(consultant_df, 30)
        total_365d, pct_365d = calculate_error_metrics(consultant_df, 365)
        
        consultant_metrics.append({
            'consultant': consultant,
            'errors_7d': total_7d,
            'errors_30d': total_30d,
            'errors_365d': total_365d,
            'error_pct': pct_7d  # Using 7-day percentage for line
        })
    
    df = pd.DataFrame(consultant_metrics)
    
    # Create figure with secondary y-axis
    fig = go.Figure()
    
    # Add bars for different periods
    bar_colors = ['lightblue', 'royalblue', 'darkblue']
    periods = [('7d', '7 Days'), ('30d', '30 Days'), ('365d', '365 Days')]
    
    for (period, label), color in zip(periods, bar_colors):
        fig.add_trace(go.Bar(
            x=df['consultant'],
            y=df[f'errors_{period}'],
            name=f'Errors {label}',
            marker_color=color
        ))
    
    # Add line for error percentage
    fig.add_trace(go.Scatter(
        x=df['consultant'],
        y=df['error_pct'],
        name='Error %',
        yaxis='y2',
        line=dict(color='red', width=2)
    ))
    
    fig.update_layout(
        title='Consultant Error Analysis',
        xaxis_title='Consultant',
        yaxis_title='Error Count',
        yaxis2=dict(
            title='Error %',
            overlaying='y',
            side='right',
            range=[0, 100]
        ),
        barmode='group',
        height=600,
        showlegend=True
    )
    
    return fig.to_json()

def generate_parameter_error_chart(claim_audit_df):
    # Calculate error counts by parameter
    parameter_error_df = claim_audit_df.groupby('parameter_stage').agg({
        'total': 'sum',
        'met': 'sum'  
    }).reset_index()
    parameter_error_df['error_count'] = parameter_error_df['total'] - parameter_error_df['met']

    # Create bar chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=parameter_error_df['parameter_stage'],
        y=parameter_error_df['error_count'],
        name='Error Count',
        marker_color='indianred'
    ))

    fig.update_layout(
        title='Parameter Error Analysis',
        xaxis_title='Parameter',
        yaxis_title='Error Count',
        height=600,
        showlegend=True
    )
    
    return fig.to_json()

def generate_parameter_comments_treemap(claim_audit_df):
    # Calculate error counts by parameter comments
    comment_error_df = claim_audit_df[claim_audit_df['parameter_score_ai'] == 'Not Met'].groupby(
        'parameter_comments'
    ).size().reset_index(name='error_count')

    # Create treemap
    fig = go.Figure(go.Treemap(
        labels=comment_error_df['parameter_comments'],
        parents=[""] * len(comment_error_df),  # Root level
        values=comment_error_df['error_count'],
        textinfo="label+value",
        marker=dict(
            colors=comment_error_df['error_count'],
            colorscale='RdBu',
            showscale=True
        )
    ))

    fig.update_layout(
        title='Error Distribution by Parameter Comments',
        width=800,
        height=600
    )

    return fig.to_json()

def calculate_dashboard_metrics(claim_audit_df):
    metrics = {
        'claims_monitored_count': len(claim_audit_df['claim__claim_id'].unique()),
        
        'total_opportunities_identified': len(claim_audit_df[
            claim_audit_df['parameter_score_ai'].isin(['Met', 'Not Met'])
        ]),
        
        'total_errors_identified': len(claim_audit_df[
            claim_audit_df['parameter_score_ai'] == 'Not Met'
        ]),
        
        'file_review_score': int(
            (claim_audit_df['met'].sum() / claim_audit_df['total'].sum() * 100)
            if claim_audit_df['total'].sum() > 0 else 0
        )
    }
    
    return metrics


def filter_data_file_review(request):
    filters = {
        'line_of_business': request.GET.get('line_of_business'),
        'subline_of_business': request.GET.get('subline_of_business'),
        'nature_of_loss': request.GET.get('nature_of_loss'),  # claims
        'cause_of_loss': request.GET.get('cause_of_loss'),  # claims
        'audit_status': request.GET.get('audit_status'),  # claims
        'leakage_type': request.GET.get('leakage_type'),
        'claim_state': request.GET.get('claim_state'),
        'claim_consultant': request.GET.get('claim_consultant'),
        'team': request.GET.get('team'),
        'brand': request.GET.get('brand'),
        'parameter_category': request.GET.get('parameter_category'),
        'parameter_name': request.GET.get('parameter_name'),
        'quality_auditor': request.GET.get('quality_auditor'),
        'monitoring_start_date': request.GET.get('monitoring_start_date'),
        'monitoring_end_date': request.GET.get('monitoring_end_date'),
        'loss_start_date': request.GET.get('loss_start_date'),
        'loss_end_date': request.GET.get('loss_end_date'),
        'close_start_date': request.GET.get('close_start_date'),
        'close_end_date': request.GET.get('close_end_date')
    }
    print("The filters :\n" , filters)
    # Build the query
    query = Q()
    if filters['line_of_business'] and filters['line_of_business'] != 'All':
        query &= Q(claim__lob=filters['line_of_business'])
    if filters['claim_state'] and filters['claim_state'] != 'All':
        query &= Q(claim__claim_status=filters['claim_state'])
    if filters['subline_of_business'] and filters['subline_of_business'] != 'All':
        query &= Q(claim__subline_of_business=filters['subline_of_business'])
    if filters['nature_of_loss'] and filters['nature_of_loss'] != 'All':
        query &= Q(claim__general_nature_of_loss=filters['nature_of_loss'])
    if filters['cause_of_loss'] and filters['cause_of_loss'] != 'All':
        query &= Q(claim__loss_claim_cause=filters['cause_of_loss'])
    if filters['audit_status'] and filters['audit_status'] != 'All':
        query &= Q(claim__audit_status=filters['audit_status'])
    if filters['leakage_type'] and filters['leakage_type'] != 'All':
        query &= Q(leakage_type=filters['leakage_type'])
    if filters['claim_consultant'] and filters['claim_consultant'] != 'All':
        query &= Q(claim__claim_consultant=filters['claim_consultant'])
    if filters['team'] and filters['team'] != 'All':
        query &= Q(claim__team=filters['team'])
    if filters['brand'] and filters['brand'] != 'All':
        query &= Q(claim__brand=filters['brand'])
    if filters['parameter_category'] and filters['parameter_category'] != 'All':
        query &= Q(parameter__parameter_category=filters['parameter_category'])
    if filters['parameter_name'] and filters['parameter_name'] != 'All':
        query &= Q(parameter__parameter_name=filters['parameter_name'])
    if filters['quality_auditor'] and filters['quality_auditor'] != 'All':
        query &= Q(claim__response_submitted_by=filters['quality_auditor'])
    if filters['monitoring_start_date'] and filters['monitoring_end_date']:
        query &= Q(audit_date__range=[filters['monitoring_start_date'], filters['monitoring_end_date']])
    if filters['loss_start_date'] and filters['loss_end_date']:
        query &= Q(claim__loss_date__range=[filters['loss_start_date'], filters['loss_end_date']])
    if filters['close_start_date'] and filters['close_end_date']:
        query &= Q(claim__close_date__range=[filters['close_start_date'], filters['close_end_date']])

    # Query the database
    claim_auditables = ClaimAuditable.objects.select_related(
        'claim', 
        'parameter'
    ).prefetch_related(
        'claim__dsoutcomes'
    ).filter(query)

    # Paginate the response
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 1000))
    start = (page - 1) * page_size
    end = start + page_size

    # Prepare the response data
    response_data = {
        'claim_audit_data': [
            {
                'claim__claim_id': audit.claim.claim_id,
                'audit_date' : audit.audit_date,
                'parameter_score_ai': audit.parameter_score_ai,
                'total': audit.total,
                'met': audit.met,
                'parameter_stage' : audit.parameter.parameter_stage,
                'consultant_name': audit.claim.dsoutcomes.first().consultant_name if audit.claim.dsoutcomes.exists() else None,
                'parameter_comments' : audit.parameter_comments
            }
            for audit in claim_auditables[start:end]
        ],
        'total_records': claim_auditables.count(),
        'page': page,
        'page_size': page_size,
    }
    return response_data
    return JsonResponse(response_data, safe=False)

def generate_graphs(request):
    # Get the filtered data
    filtered_data = filter_data_file_review(request)
    # filtered_data = pd.DataFrame(filtered_data)

    print("The filtered data is ====\n", filtered_data)
    claim_audit_df = pd.DataFrame(filtered_data.get('claim_audit_data'))
    print(claim_audit_df.head())
# Generate the graph
    
    if 'audit_date' in claim_audit_df.columns :
        # Convert audit_date to datetime and extract year, quarter, month, day
        claim_audit_df['audit_date'] = pd.to_datetime(claim_audit_df['audit_date'])
        claim_audit_df['year'] = claim_audit_df['audit_date'].dt.year
        claim_audit_df['quarter'] = claim_audit_df['audit_date'].dt.to_period('Q')
        claim_audit_df['month'] = claim_audit_df['audit_date'].dt.to_period('M')
        claim_audit_df['day'] = claim_audit_df['audit_date'].dt.date

        # Calculate ERROR COUNT NEW and FILE REVIEW SCORE
        claim_audit_df['total'] = claim_audit_df['total'].astype(float)
        claim_audit_df['met'] = claim_audit_df['met'].astype(float)
        claim_audit_df['error_count_new'] = claim_audit_df['total'] - claim_audit_df['met']
        claim_audit_df['file_review_score'] = claim_audit_df['met'] / claim_audit_df['total']

        # Group by year, quarter, month, day
        grouped_df = claim_audit_df.groupby(['year', 'quarter', 'month', 'day']).agg({
            'error_count_new': 'sum',
            'file_review_score': 'mean'
        }).reset_index()

        # Create the bar and line graph
        fig = go.Figure()

        # Bar graph for error count
        fig.add_trace(go.Bar(
            x=grouped_df['day'],
            y=grouped_df['error_count_new'],
            name='Error Count',
            marker_color='indianred'
        ))

        # Line graph for file review score
        fig.add_trace(go.Scatter(
            x=grouped_df['day'],
            y=grouped_df['file_review_score'],
            name='File Review Score %',
            mode='lines+markers',
            marker_color='blue'
        ))

        fig.update_layout(
            title='Error Count and File Review Score by Day',
            xaxis_title='Day',
            yaxis_title='Count / Score',
            xaxis=dict(type='category'),
            barmode='group'
        )

        # Return the graph as JSON
        bar_line_graph_json = fig.to_json()
        print("The graph is ================\n", bar_line_graph_json)
    # Generate the pie chart
    pie_chart_json = None
    if 'parameter_stage' in claim_audit_df.columns:
        pie_df = claim_audit_df.groupby('parameter_stage').agg({
            'total': 'sum',
            'met': 'sum'
        }).reset_index()

        pie_df['error_count_new'] = pie_df['total'] - pie_df['met']

        pie_fig = go.Figure(data=[go.Pie(
            labels=pie_df['parameter_stage'],
            values=pie_df['error_count_new'],
            hole=.3
        )])

        pie_fig.update_layout(
            title='Error Count by Parameter Stage'
        )

        # Convert the pie chart to JSON
        pie_chart_json = pie_fig.to_json()
    treemap_json = None
    if 'consultant_name' in claim_audit_df.columns:
        # Calculate error counts by consultant
        consultant_error_df = claim_audit_df.groupby('consultant_name').agg({
            'total': 'sum',
            'met' : 'sum'  
        }).reset_index()
        consultant_error_df['error_count_new'] = consultant_error_df['total'] - consultant_error_df['met']

        # Create treemap
        treemap_fig = go.Figure(go.Treemap(
            labels=consultant_error_df['consultant_name'],
            parents=[""] * len(consultant_error_df),  # Root level
            values=consultant_error_df['error_count_new'],
            textinfo="label+value",
            marker=dict(
                colors=consultant_error_df['error_count_new'],
                colorscale='RdBu',
                showscale=True
            )
        ))

        treemap_fig.update_layout(
            title='Error Count by Claim Consultant',
            width=800,
            height=600
        )

        # Convert to JSON
        treemap_json = treemap_fig.to_json()
      # In generate_graphs function:
    consultant_error_chart = None
    if 'consultant_name' in claim_audit_df.columns:
        consultant_error_chart = generate_consultant_error_chart(claim_audit_df)
    
    # In generate_graphs function:
    parameter_error_chart = None
    if 'parameter_stage' in claim_audit_df.columns:
        parameter_error_chart = generate_parameter_error_chart(claim_audit_df)
    # In generate_graphs function:
    parameter_comments_treemap = None
    if 'parameter_comments' in claim_audit_df.columns:
        parameter_comments_treemap = generate_parameter_comments_treemap(claim_audit_df)
    # In generate_graphs function:
    dashboard_metrics = calculate_dashboard_metrics(claim_audit_df)

    # Return the JSON response with the calculated values and graphs
    return JsonResponse({
        'bar_line_graph': bar_line_graph_json,
        'pie_chart': pie_chart_json,
        'treemap': treemap_json,
        'bar_graph': consultant_error_chart,
        'param_bar_graph': parameter_error_chart,
        'com_treemap': parameter_comments_treemap,
        **dashboard_metrics
    }, safe=False)