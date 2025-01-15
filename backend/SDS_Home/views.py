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

def filter_data_home_page1(request):
    # Extract query parameters
    filters = {
        # 'lob': request.GET.get('lob'),
        'lob': request.GET.getlist('line_of_business', []),
        'monitoring_start_date': request.GET.get('start_date'),
        'monitoring_end_date': request.GET.get('end_date'),
        # 'monitoring_start_date': request.GET.get('monitoring_start_date'),
        # 'monitoring_end_date': request.GET.get('monitoring_end_date'),
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
    
    # Paginate
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 1000))
    start = (page - 1) * page_size
    end = start + page_size
    
# Prepare data for plotting
    data = [
        {
            # 'claim_id': outcome.claim.claim_id,
            # 'lob': outcome.claim.lob.line_of_business,
            'signal_generated_date': outcome.claim.audits.first().audit_date.date() if outcome.claim.audits.exists() else None,
            'stored_leakage_rate_new': outcome.stored_leakage_rate_new if outcome.stored_leakage_rate_new else 0,
        }
        for outcome in outcomes
    ]
    
    df = pd.DataFrame(data)

    df['signal_generated_date'] = pd.to_datetime(df['signal_generated_date'])

    df_aggregated = df.groupby('signal_generated_date').mean().reset_index()

    # df_aggregated['formatted_date'] = df_aggregated['signal_generated_date'].apply(
    #     lambda x: f"{x.year} Qtr {((x.month-1)//3)+1} {x.strftime('%B')}"
    # )
    df_aggregated['formatted_date'] = df_aggregated['signal_generated_date'].apply(
        lambda x: x.strftime('%Y-%m-%d')
    )
    
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
            tickformat='%Y-%q-%m-%d',
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
    
    # Convert audit_date to datetime
    df['audit_date'] = pd.to_datetime(df['audit_date'])
    
    # Aggregate data by audit_date
    df_aggregated = df.groupby('audit_date').mean().reset_index()
    
    # Create custom date format for x-axis labels
    # df_aggregated['formatted_date'] = df_aggregated['audit_date'].apply(
    #     lambda x: f"{x.year} Qtr {((x.month-1)//3)+1} {x.strftime('%B')}"
    # )
    df_aggregated['formatted_date'] = df_aggregated['audit_date'].apply(
        lambda x: x.strftime('%Y-%m-%d')
    )
    
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


# # Create your views here.
# def get_leakage_data(request):
#         # Fetch data from CSVs (or database)
#         data_ds = pd.read_csv("C:/Users/abhishek221057/Downloads/dsoutcome_1aug_31aug_seq10.csv",low_memory=False)
#         data_ds = data_ds[['CLAIM ID', 'CREATED DATE', 'FINAL LEAKAGE AMOUNT', 'POTENTIAL LEAKAGE AMOUNT']]
#         data_claim = pd.read_csv("C:/Users/abhishek221057/Downloads/claimauditable_1aug_31aug_seq10.csv", low_memory=False)
#         data_claim = data_claim[['CLAIM ID', 'FINAL LOB']]
#         # print("Filres read")
#         # Merge dataframes
#         data_ds = data_ds.merge(data_claim[['CLAIM ID', 'FINAL LOB']], on='CLAIM ID', how='left')
#         # print("Merging Completed")
#         # Apply filters (example: by date range and 'LINE OF BUSINESS')
#         min_date, max_date = data_ds['CREATED DATE'].min(), data_ds['CREATED DATE'].max()
#         start_date = request.GET.get('start_date', min_date)
#         end_date = request.GET.get('end_date', max_date)
        
#         filtered_data = data_ds[data_ds['CREATED DATE'].between(start_date, end_date)]
        
#         # Add more filters as needed
#         line_of_business = request.GET.getlist('line_of_business', [])
#         if line_of_business:
#             filtered_data = filtered_data[filtered_data['FINAL LOB'].isin(line_of_business)]
#         # print("filters Applied")
#         # page_number = request.GET.get('page', 1)  # Default page is 1 if not provided
#         # page_size = request.GET.get('page_size', 100)  # Default page size is 100 if not provided

#         # paginator = Paginator(data_ds, page_size)  # Paginate the data
#         # page = paginator.get_page(page_number)

#         # # Prepare the paginated data as a response
#         # response_data = {
#         #     'total_pages': paginator.num_pages,
#         #     'current_page': page.number,
#         #     'total_records': paginator.count,
#         #     'data': page.object_list.to_dict(orient='records'),  # Convert DataFrame to dict
#         # }

#         # Calculate Leakage Rate %
#         # print(filtered_data['FINAL LEAKAGE AMOUNT'].mean())
#         # print(filtered_data['POTENTIAL LEAKAGE AMOUNT'].mean())
#         filtered_data['FINAL LEAKAGE AMOUNT'] = filtered_data['FINAL LEAKAGE AMOUNT'].fillna(filtered_data['FINAL LEAKAGE AMOUNT'].mean())
#         filtered_data['POTENTIAL LEAKAGE AMOUNT'] = filtered_data['POTENTIAL LEAKAGE AMOUNT'].fillna(filtered_data['POTENTIAL LEAKAGE AMOUNT'].mean())
#         # filtered_data['Leakage Rate %'] = filtered_data['FINAL LEAKAGE AMOUNT'] / filtered_data.apply(
#         #     lambda row: max(row['FINAL LEAKAGE AMOUNT'] - row['POTENTIAL LEAKAGE AMOUNT'], 1), axis=1
#         # )

#         filtered_data['FINAL LEAKAGE AMOUNT'] = filtered_data['FINAL LEAKAGE AMOUNT'].astype(float)
#         filtered_data['POTENTIAL LEAKAGE AMOUNT'] = filtered_data['POTENTIAL LEAKAGE AMOUNT'].astype(float)
        
#         # Calculate the difference and handle potential issues
#         filtered_data['DIFFERENCE'] = filtered_data['FINAL LEAKAGE AMOUNT'] - filtered_data['POTENTIAL LEAKAGE AMOUNT']
#         filtered_data['DIFFERENCE'] = filtered_data['DIFFERENCE'].apply(lambda x: max(x, 1))
        
#         # Calculate Leakage Rate %
#         filtered_data['Leakage Rate %'] = filtered_data['FINAL LEAKAGE AMOUNT'] / filtered_data['DIFFERENCE']
#         # print("Generating graph")
#         # Generate the graph using Plotly
#         fig = px.line(filtered_data, x='CREATED DATE', y='Leakage Rate %', title='Leakage Rate Trend %')
#         fig_json = fig.to_json()
#         # Save the graph to a bytes buffer
#         # buf = io.BytesIO()
#         # fig.write_image(buf, format='png')
#         # buf.seek(0)
#         # graph_url = base64.b64encode(buf.read()).decode('utf-8')
#         # buf.close()
#         # print("Graph generated")
#         return JsonResponse({'graph': fig_json})

# def get_file_review_data(request):
#     data_claim = pd.read_csv("C:/Users/abhishek221057/Downloads/claimauditable_1aug_31aug_seq10.csv", low_memory=False)
#     data_claim = data_claim[['CLAIM ID', 'FINAL LOB', 'AUDIT DATE', 'OVERALL SCORE','PARAMETER SCORE AI']]

#     min_date, max_date = data_claim['AUDIT DATE'].min(), data_claim['AUDIT DATE'].max()
#     start_date = request.GET.get('start_date', min_date)
#     end_date = request.GET.get('end_date', max_date)
    
#     filtered_data = data_claim[data_claim['AUDIT DATE'].between(start_date, end_date)]

#     line_of_business = request.GET.getlist('line_of_business', [])
#     if line_of_business:
#         filtered_data = filtered_data[filtered_data['FINAL LOB'].isin(line_of_business)]

#      # Calculate File Review Score %
#     def calculate_file_review_score(group):
#         total_overall_score = group['OVERALL SCORE'].sum()
#         total_score_ai_met = group[group['PARAMETER SCORE AI'].lower() == 'met']['OVERALL SCORE'].sum()
#         if total_overall_score == 0:
#             return 0
#         return total_score_ai_met / total_overall_score

#     file_review_score = (
#         filtered_data.groupby('AUDIT DATE')
#         .apply(calculate_file_review_score)
#         .reset_index(drop=True)
#         .reset_index()
#     )
#     print(file_review_score)
#     file_review_score.columns = ['audit_date', 'File Review Score %']
#     # Generate the graph using Plotly
#     fig = px.line(file_review_score, x='audit_date', y='File Review Score %', title='File Review Score Trend %')
#     fig_json = fig.to_json()
    
#     return JsonResponse({'graph': fig_json})