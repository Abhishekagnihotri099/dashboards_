from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
import plotly.express as px
import io
import base64
import pandas as pd
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from backend_app.models import Claims, dsoutcome, ClaimAuditable

def format_date(date, hierarchy):
    if hierarchy == "Day-wise":
        return date.strftime('%Y-%m-%d')
    elif hierarchy == "Month-wise":
        return date.strftime('%Y-%m')
    elif hierarchy == "Quarterly":
        return f"{date.year} Q{((date.month-1)//3)+1}"
    elif hierarchy == "Yearly":
        return date.strftime('%Y')

def filter_data_home_page1(request):
    # Extract query parameters
    filters = {
        'lob': request.GET.getlist('line_of_business', []),
        'monitoring_start_date': request.GET.get('start_date'),
        'monitoring_end_date': request.GET.get('end_date'),
        'date_hierarchy': request.GET.get('date_hierarchy', 'Day-wise')
    }
    print(filters)
    
    # Build query
    query = Q()
    if filters['lob'] and 'All' not in filters['lob']:
        query &= Q(claim__lob__line_of_business__in=filters['lob'])
    if filters['monitoring_start_date'] and filters['monitoring_end_date']:
        query &= Q(claim__audits__audit_date__date__range=[
            filters['monitoring_start_date'], 
            filters['monitoring_end_date']
        ])
    
    # Query database
    outcomes = dsoutcome.objects.filter(query).select_related('claim__lob')
    
    # Prepare data for plotting
    data = [
        {
            'signal_generated_date': outcome.claim.audits.first().audit_date.date() if outcome.claim.audits.exists() else None,
            'stored_leakage_rate_new': outcome.stored_leakage_rate_new if outcome.stored_leakage_rate_new else 0,
        }
        for outcome in outcomes
    ]
    
    df = pd.DataFrame(data)
    df['signal_generated_date'] = pd.to_datetime(df['signal_generated_date'])
    df['formatted_date'] = df['signal_generated_date'].apply(lambda x: format_date(x, filters['date_hierarchy']))
    df_aggregated = df.groupby('formatted_date').mean().reset_index()
    
    # Create 2D line plot
    fig = px.line(
        df_aggregated,
        x='formatted_date',
        y='stored_leakage_rate_new',
        labels={
            'formatted_date': 'SIGNAL GENERATED DATE',
            'stored_leakage_rate_new': 'LEAKAGE RATE %'
        },
        title='Leakage Rate Trend %'
    )
    
    # Format x-axis ticks
    fig.update_layout(
        xaxis=dict(
            title='SIGNAL GENERATED DATE'
        ),
        yaxis=dict(
            title='LEAKAGE RATE %'
        )
    )
    
    fig_json = fig.to_json()
    return JsonResponse({'graph': fig_json})

def filter_data_home_page2(request):
    # Extract query parameters
    filters = {
        'lob': request.GET.getlist('line_of_business', []),
        'monitoring_start_date': request.GET.get('start_date'),
        'monitoring_end_date': request.GET.get('end_date'),
        'date_hierarchy': request.GET.get('date_hierarchy', 'Day-wise')
    }
    print(filters)
    
    # Build query
    query = Q()
    if filters['lob'] and 'All' not in filters['lob']:
        query &= Q(claim__lob__line_of_business__in=filters['lob'])
    if filters['monitoring_start_date'] and filters['monitoring_end_date']:
        query &= Q(audit_date__date__range=[
            filters['monitoring_start_date'], 
            filters['monitoring_end_date']
        ])
    
    # Query database
    audits = ClaimAuditable.objects.filter(query).select_related('claim__lob')
    
    # Prepare data for plotting
    data = [
        {
            'audit_date': audit.audit_date.date() if audit.audit_date else None,
            'stored_file_review_score': audit.file_review_score if audit.file_review_score else 0,
        }
        for audit in audits
    ]
    
    df = pd.DataFrame(data)
    df['audit_date'] = pd.to_datetime(df['audit_date'])
    df['formatted_date'] = df['audit_date'].apply(lambda x: format_date(x, filters['date_hierarchy']))
    df_aggregated = df.groupby('formatted_date').mean().reset_index()
    
    # Create 2D line plot
    fig = px.line(
        df_aggregated,
        x='formatted_date',
        y='stored_file_review_score',
        labels={
            'formatted_date': 'AUDIT DATE',
            'stored_file_review_score': 'FILE REVIEW SCORE %'
        },
        title='File Review Score Trend %'
    )
    
    # Format x-axis ticks
    fig.update_layout(
        xaxis=dict(
            title='AUDIT DATE'
        ),
        yaxis=dict(
            title='FILE REVIEW SCORE %'
        )
    )
    
    fig_json = fig.to_json()
    return JsonResponse({'graph': fig_json})