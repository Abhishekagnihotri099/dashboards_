from django.shortcuts import render
from django.http import JsonResponse
import pandas as pd
from django.conf import settings
import os
from django.core.cache import cache
import logging
import plotly.graph_objects as go
import base64
from io import BytesIO

logger = logging.getLogger(__name__)

def filter_data_file_review(request):
    # Extract query parameters from the request
    response_data = cache.get('response_data')
    # if response_data is not None:
    #     return response_data
    filters = {
        'line_of_business': request.GET.get('line_of_business'),
        'subline_of_business': request.GET.get('subline_of_business'),
        'nature_of_loss': request.GET.get('nature_of_loss'),
        'cause_of_loss': request.GET.get('cause_of_loss'),
        'audit_status': request.GET.get('audit_status'),
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

    # Define the paths to the CSV files
    claim_audit_file_path = os.path.join(settings.BASE_DIR, 'backend_app/claimauditable_0.1.csv')
    claims_file_path = os.path.join(settings.BASE_DIR, 'backend_app/claims_0.1.csv')
    parameter_file_path = os.path.join(settings.BASE_DIR, 'backend_app/parameters_0.1.csv')

    # Check if DataFrames are cached
    claim_audit_df = cache.get('claim_audit_df')
    claims_df = cache.get('claims_df')
    parameter_df = cache.get('parameter_df')

    # If not cached, read the CSV files and cache the DataFrames
    if claim_audit_df is None:
        claim_audit_df = pd.read_csv(claim_audit_file_path, low_memory=False)
        cache.set('claim_audit_df', claim_audit_df, timeout=60*60)  # Cache for 1 hour

    if claims_df is None:
        claims_df = pd.read_csv(claims_file_path, low_memory=False)
        cache.set('claims_df', claims_df, timeout=60*60)  # Cache for 1 hour

    if parameter_df is None:
        parameter_df = pd.read_csv(parameter_file_path, low_memory=False)
        cache.set('parameter_df', parameter_df, timeout=60*60)  # Cache for 1 hour

    logger.info("Data read successfully")

    # Apply filters to the DataFrames
    for key, value in filters.items():
        if value and value.lower() != 'all':
            if key in claim_audit_df.columns:
                claim_audit_df = claim_audit_df[claim_audit_df[key] == value]
            if key in claims_df.columns:
                claims_df = claims_df[claims_df[key] == value]
            if key in parameter_df.columns:
                parameter_df = parameter_df[parameter_df[key] == value]
    # Apply date range filters
    if filters['monitoring_start_date'] and filters['monitoring_end_date']:
        claim_audit_df['AUDIT DATE'] = pd.to_datetime(claim_audit_df['AUDIT DATE'])
        claim_audit_df = claim_audit_df[
            (claim_audit_df['AUDIT DATE'] >= filters['monitoring_start_date']) &
            (claim_audit_df['AUDIT DATE'] <= filters['monitoring_end_date'])
        ]

    if filters['loss_start_date'] and filters['loss_end_date']:
        claims_df['loss_date'] = pd.to_datetime(claims_df['loss_date'])
        claims_df = claims_df[
            (claims_df['loss_date'] >= filters['loss_start_date']) &
            (claims_df['loss_date'] <= filters['loss_end_date'])
        ]

    if filters['close_start_date'] and filters['close_end_date']:
        claims_df['close_date'] = pd.to_datetime(claims_df['close_date'])
        claims_df = claims_df[
            (claims_df['close_date'] >= filters['close_start_date']) &
            (claims_df['close_date'] <= filters['close_end_date'])
        ]
# Merge DataFrames based on common columns
    merged_df = claim_audit_df.merge(claims_df, left_on='CLAIM ID', right_on='claim_id', how='left')
    merged_df = merged_df.merge(parameter_df, left_on='PARAMETER ID', right_on='parameter_id', how='left')

    # Paginate the response
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 1000))
    start = (page - 1) * page_size
    end = start + page_size

    # Combine data (example, adjust based on your needs)
    response_data = {
        'claim_audit_data': merged_df.iloc[start:end].to_dict(orient='records'),
        'total_records': len(merged_df),
        'page': page,
        'page_size': page_size,
    }

    cache.set('response_data', response_data, timeout=60*60)  # Cache for 1 hour

    logger.info("Data filtered successfully")
    
    return response_data

def generate_graphs(request):
    # Get the filtered data
    filtered_data = filter_data_file_review(request)
    claim_audit_df = pd.DataFrame(filtered_data['claim_audit_data'])

    # Generate the graph
    if 'AUDIT DATE' in claim_audit_df.columns and 'OVERALL SCORE' in claim_audit_df.columns:
        # Convert AUDIT DATE to datetime and extract year
        claim_audit_df['AUDIT DATE'] = pd.to_datetime(claim_audit_df['AUDIT DATE'])
        claim_audit_df['year'] = claim_audit_df['AUDIT DATE'].dt.year

        # Group by year
        grouped_df = claim_audit_df.groupby('year').agg({
            'OVERALL SCORE': ['count', 'mean']
        }).reset_index()
        grouped_df.columns = ['year', 'error_count', 'average_OVERALL SCORE']

        # Create the bar and line graph
        fig = go.Figure()

        # Bar graph for error count
        fig.add_trace(go.Bar(
            x=grouped_df['year'],
            y=grouped_df['error_count'],
            name='Error Count',
            marker_color='indianred'
        ))

        # Line graph for average overall score
        fig.add_trace(go.Scatter(
            x=grouped_df['year'],
            y=grouped_df['average_OVERALL SCORE'],
            name='Average Overall Score %',
            mode='lines+markers',
            marker_color='blue'
        ))
        # Line graph for error percentage
        fig.add_trace(go.Scatter(
            x=grouped_df['year'],
            y=grouped_df['average_OVERALL SCORE'],
            name='Error Percentage',
            mode='lines+markers',
            marker_color='green',
            yaxis='y3'  # Specify the secondary y-axis
        ))

        fig.update_layout(
            title='Error Count and Average Overall Score by Year',
            xaxis_title='Year',
            yaxis_title='Count / Score',
            xaxis=dict(type='category'),
            yaxis3=dict(
                title='Error Percentage',
                overlaying='y',
                side='right',
                position= 1  # Adjust the position of the secondary y-axis
            ),
            barmode='group'
        )

        # Return the graph as JSON
        bar_line_graph_json = fig.to_json()
    # Generate the pie chart
    if 'PARAMETER STAGE' in claim_audit_df.columns:
        pie_df = claim_audit_df.groupby('PARAMETER STAGE').size().reset_index(name='error_count')

        pie_fig = go.Figure(data=[go.Pie(
            labels=pie_df['PARAMETER STAGE'],
            values=pie_df['error_count'],
            hole=.3
        )])

        pie_fig.update_layout(
            title='Error Count by PARAMETER STAGE'
        )

        # Convert the pie chart to JSON
        pie_chart_json = pie_fig.to_json()
        # Generate the treemap for claim consultant counts
        if 'RESPONSE ASSIGNED AUDITOR' in claim_audit_df.columns:
            consultant_df = claim_audit_df['RESPONSE ASSIGNED AUDITOR'].value_counts().reset_index()
            consultant_df.columns = ['claim_consultant', 'count']

            treemap_fig = go.Figure(go.Treemap(
                labels=consultant_df['claim_consultant'],
                parents=[""] * len(consultant_df),
                values=consultant_df['count'],
                textinfo="label+value+percent entry",
                marker=dict(colors=consultant_df['count'], colorscale='Viridis')
            ))

            treemap_fig.update_layout(
                title='Claim Consultant Counts'
            )

            # Convert the treemap to JSON
            treemap_json = treemap_fig.to_json()
        # Generate the bar graph for consultant counts and error percentage
    if 'RESPONSE ASSIGNED AUDITOR' in claim_audit_df.columns and 'OVERALL SCORE' in claim_audit_df.columns:
        consultant_error_df = claim_audit_df.groupby('RESPONSE ASSIGNED AUDITOR').agg(
            average_overall_score=('OVERALL SCORE', 'mean'),
            count=('RESPONSE ASSIGNED AUDITOR', 'size')
        ).reset_index()
        consultant_error_df['error_percentage'] = 100 - consultant_error_df['average_overall_score']

        bar_fig = go.Figure()

        # Bar graph for consultant counts
        bar_fig.add_trace(go.Bar(
            x=consultant_error_df['RESPONSE ASSIGNED AUDITOR'],
            y=consultant_error_df['count'],
            name='Count',
            marker_color='indianred'
        ))

        # Bar graph for error percentage
        bar_fig.add_trace(go.Bar(
            x=consultant_error_df['RESPONSE ASSIGNED AUDITOR'],
            y=consultant_error_df['error_percentage'],
            name='Error Percentage',
            marker_color='blue'
        ))

        bar_fig.update_layout(
            title='Consultant Counts and Error Percentage',
            xaxis_title='Consultant',
            yaxis_title='Count / Error Percentage',
            barmode='group'
        )

        # Convert the bar graph to JSON
        bar_graph_json = bar_fig.to_json()
    if 'PARAMETER NAME' in claim_audit_df.columns and 'OVERALL SCORE' in claim_audit_df.columns:
        consultant_error_df = claim_audit_df.groupby('PARAMETER NAME').agg(
            average_overall_score=('OVERALL SCORE', 'mean'),
            count=('PARAMETER NAME', 'size')
        ).reset_index()
        consultant_error_df['error_percentage'] = 100 - consultant_error_df['average_overall_score']

        bar_fig = go.Figure()

        # Bar graph for consultant counts
        bar_fig.add_trace(go.Bar(
            x=consultant_error_df['PARAMETER NAME'],
            y=consultant_error_df['count'],
            name='Count',
            marker_color='indianred'
        ))

        # Bar graph for error percentage
        bar_fig.add_trace(go.Bar(
            x=consultant_error_df['PARAMETER NAME'],
            y=consultant_error_df['error_percentage'],
            name='Error Percentage',
            marker_color='blue'
        ))

        bar_fig.update_layout(
            title='Consultant Counts and Error Percentage',
            xaxis_title='Consultant',
            yaxis_title='Count / Error Percentage',
            barmode='group'
        )

        # Convert the bar graph to JSON
        param_bar_graph_json = bar_fig.to_json()
    # Generate the treemap for claim consultant counts
        if 'PARAMETER COMMENTS' in claim_audit_df.columns:
            comment_df = claim_audit_df['PARAMETER COMMENTS'].value_counts().reset_index()
            comment_df.columns = ['comments', 'count']

            com_treemap_fig = go.Figure(go.Treemap(
                labels=comment_df['comments'],
                parents=[""] * len(comment_df),
                values=comment_df['count'],
                textinfo="label+value+percent entry",
                marker=dict(colors=consultant_df['count'], colorscale='Viridis')
            ))

            com_treemap_fig.update_layout(
                title='Claim Consultant Counts'
            )

            # Convert the treemap to JSON
            com_treemap_fig_json = com_treemap_fig.to_json()

       
        
    # Calculate values for the cards
    claims_monitored_count = claim_audit_df['CLAIM ID'].nunique()
    print("DJ", claims_monitored_count)
    total_opportunities_identified = claim_audit_df[
        claim_audit_df['PARAMETER FINAL SCORE'].isin(['Met', 'Not Met'])
    ]['PARAMETER FINAL SCORE'].count()

    total_errors_identified = claim_audit_df[
        claim_audit_df['PARAMETER FINAL SCORE'] == 'Not Met'
    ]['PARAMETER FINAL SCORE'].count()

    file_review_score = (claim_audit_df[claim_audit_df['PARAMETER FINAL SCORE'] == 'Met']['PARAMETER FINAL SCORE'].count() / claim_audit_df['PARAMETER FINAL SCORE'].count()) if claim_audit_df['PARAMETER FINAL SCORE'].count() != 0 else 0
    # Return the JSON response with the calculated values and graphs
    return JsonResponse({
        'bar_line_graph': bar_line_graph_json,
        'pie_chart': pie_chart_json,
        'treemap': treemap_json,
        'bar_graph': bar_graph_json,
        'param_bar_graph':param_bar_graph_json,
        'com_treemap':com_treemap_fig_json,
        'claims_monitored_count': int(claims_monitored_count),
        'total_opportunities_identified': int(total_opportunities_identified),
        'total_errors_identified': int(total_errors_identified),
        'file_review_score': int(file_review_score)
    }, safe=False)

