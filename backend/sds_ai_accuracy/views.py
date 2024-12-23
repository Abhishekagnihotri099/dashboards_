# filepath: /C:/Users/digvijay221046/Desktop/Git-AG-DJ/dashboards_/backend/ai_accuracy/views.py
from django.shortcuts import render
from django.http import JsonResponse
import pandas as pd
import os
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

def filter_data_ai_accuracy(request):
    # Extract query parameters from the request
    filters = {
        'ai_monitoring_date': request.GET.get('ai_monitoring_date'),
        'manual_monitoring_date': request.GET.get('manual_monitoring_date'),
        'parameter_name': request.GET.get('parameter_name'),
        'leakage_category': request.GET.get('leakage_category'),
        'line_of_business': request.GET.get('line_of_business'),
        'audited_by': request.GET.get('audited_by'),
        'ai_output': request.GET.get('ai_output'),
    }

    # Define the paths to the CSV files
    claim_audit_file_path = os.path.join(settings.BASE_DIR, 'backend_app/claimauditable_0.1.csv')
    dsoutcome_history_file_path = os.path.join(settings.BASE_DIR, 'backend_app/dsoutcome_0.1.csv')
    parameter_file_path = os.path.join(settings.BASE_DIR, 'backend_app/parameters_0.1.csv')

    # Check if DataFrames are cached
    claim_audit_df = cache.get('claim_audit_df')
    dsoutcome_history_df = cache.get('dsoutcome_history_df')
    parameter_df = cache.get('parameter_df')

    # If not cached, read the CSV files and cache the DataFrames
    if claim_audit_df is None:
        claim_audit_df = pd.read_csv(claim_audit_file_path, low_memory=False)
        cache.set('claim_audit_df', claim_audit_df, timeout=60*60)  # Cache for 1 hour

    if dsoutcome_history_df is None:
        dsoutcome_history_df = pd.read_csv(dsoutcome_history_file_path, low_memory=False)
        cache.set('dsoutcome_history_df', dsoutcome_history_df, timeout=60*60)  # Cache for 1 hour

    if parameter_df is None:
        parameter_df = pd.read_csv(parameter_file_path, low_memory=False)
        cache.set('parameter_df', parameter_df, timeout=60*60)  # Cache for 1 hour

    logger.info("Data read successfully")

    # Apply filters to the DataFrames
    for key, value in filters.items():
        if value and value.lower() != 'all':
            if key in claim_audit_df.columns:
                claim_audit_df = claim_audit_df[claim_audit_df[key] == value]
            if key in dsoutcome_history_df.columns:
                dsoutcome_history_df = dsoutcome_history_df[dsoutcome_history_df[key] == value]
            if key in parameter_df.columns:
                parameter_df = parameter_df[parameter_df[key] == value]

    # Apply date range filters
    if filters['ai_monitoring_date']:
        claim_audit_df['AUDIT DATE'] = pd.to_datetime(claim_audit_df['AUDIT DATE'])
        claim_audit_df = claim_audit_df[
            (claim_audit_df['AUDIT DATE'] >= filters['ai_monitoring_date'])
        ]

    if filters['manual_monitoring_date']:
        claim_audit_df['PARAMETER AUDIT DATE'] = pd.to_datetime(claim_audit_df['PARAMETER AUDIT DATE'])
        claim_audit_df = claim_audit_df[
            (claim_audit_df['PARAMETER AUDIT DATE'] >= filters['manual_monitoring_date'])
        ]

    # Merge DataFrames based on common columns
    merged_df = claim_audit_df.merge(dsoutcome_history_df, left_on='CLAIM ID', right_on='CLAIM ID', how='inner')
    print(merged_df.columns)
    merged_df = merged_df.merge(parameter_df, left_on='parameter_id', right_on='parameter_id', how='inner')

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

    logger.info("Data filtered successfully")

    return response_data

def calculate_ai_accuracy(group):
    accuracy_numerator = group['Accuracy_Numerator'].sum()
    accuracy_denominator = group['Accuracy_Denominator'].sum()
    return (accuracy_numerator / accuracy_denominator) * 100 if accuracy_denominator != 0 else 0

def ai_accuracy_view(request):
    # Get the filtered data
    filtered_data = filter_data_ai_accuracy(request)
    claim_audit_df = pd.DataFrame(filtered_data['claim_audit_data'])

    # Calculate values for the cards
    claims_monitored_by_ai = int(claim_audit_df['CLAIM ID'].nunique())
    claims_monitored_manually = int(claim_audit_df[
        claim_audit_df['PARAMETER SCORE'].isin(['Met', 'Not Met', 'NA', 'Not Applicable'])
    ]['CLAIM ID'].nunique())
    percent_claims_monitored_manually = (claims_monitored_manually / claims_monitored_by_ai) * 100 if claims_monitored_by_ai != 0 else 0
    ai_accuracy = calculate_ai_accuracy(claim_audit_df)

    # Generate the graph
    if 'AUDIT DATE' in claim_audit_df.columns and 'AI_ACCURACY%' in claim_audit_df.columns:
        # Convert AUDIT DATE to datetime and extract year
        claim_audit_df['AUDIT DATE'] = pd.to_datetime(claim_audit_df['AUDIT DATE'])
        claim_audit_df['year'] = claim_audit_df['AUDIT DATE'].dt.year

        # Group by year
        grouped_df = claim_audit_df.groupby('year').agg({
            'AI_ACCURACY%': 'mean'
        }).reset_index()
        grouped_df.columns = ['year', 'average_AI_ACCURACY%']

        # Create the line graph
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=grouped_df['year'],
            y=grouped_df['average_AI_ACCURACY%'],
            name='Average AI Accuracy %',
            mode='lines+markers',
            marker_color='blue'
        ))

        fig.update_layout(
            title='AI Accuracy % by Year',
            xaxis_title='Year',
            yaxis_title='Average AI Accuracy %',
            xaxis=dict(type='category'),  # Set x-axis type to category
        )

        # Convert the line graph to JSON
        ai_accuracy_graph_json = fig.to_json()

    # Return the JSON response with the calculated values and graphs
    return JsonResponse({
        'claims_monitored_by_ai': claims_monitored_by_ai,
        'claims_monitored_manually': claims_monitored_manually,
        'percent_claims_monitored_manually': percent_claims_monitored_manually,
        'ai_accuracy': ai_accuracy,
        'ai_accuracy_graph': ai_accuracy_graph_json,
    }, safe=False)