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

# Create your views here.
def get_leakage_data(request):
        # Fetch data from CSVs (or database)
        data_ds = pd.read_csv("C:/Users/abhishek221057/Downloads/dsoutcome_1aug_31aug_seq10.csv",low_memory=False)
        data_ds = data_ds[['CLAIM ID', 'CREATED DATE', 'FINAL LEAKAGE AMOUNT', 'POTENTIAL LEAKAGE AMOUNT']]
        data_claim = pd.read_csv("C:/Users/abhishek221057/Downloads/claimauditable_1aug_31aug_seq10.csv", low_memory=False)
        data_claim = data_claim[['CLAIM ID', 'FINAL LOB']]
        # print("Filres read")
        # Merge dataframes
        data_ds = data_ds.merge(data_claim[['CLAIM ID', 'FINAL LOB']], on='CLAIM ID', how='left')
        # print("Merging Completed")
        # Apply filters (example: by date range and 'LINE OF BUSINESS')
        min_date, max_date = data_ds['CREATED DATE'].min(), data_ds['CREATED DATE'].max()
        start_date = request.GET.get('start_date', min_date)
        end_date = request.GET.get('end_date', max_date)
        
        filtered_data = data_ds[data_ds['CREATED DATE'].between(start_date, end_date)]
        
        # Add more filters as needed
        line_of_business = request.GET.getlist('line_of_business', [])
        if line_of_business:
            filtered_data = filtered_data[filtered_data['FINAL LOB'].isin(line_of_business)]
        # print("filters Applied")
        # page_number = request.GET.get('page', 1)  # Default page is 1 if not provided
        # page_size = request.GET.get('page_size', 100)  # Default page size is 100 if not provided

        # paginator = Paginator(data_ds, page_size)  # Paginate the data
        # page = paginator.get_page(page_number)

        # # Prepare the paginated data as a response
        # response_data = {
        #     'total_pages': paginator.num_pages,
        #     'current_page': page.number,
        #     'total_records': paginator.count,
        #     'data': page.object_list.to_dict(orient='records'),  # Convert DataFrame to dict
        # }

        # Calculate Leakage Rate %
        # print(filtered_data['FINAL LEAKAGE AMOUNT'].mean())
        # print(filtered_data['POTENTIAL LEAKAGE AMOUNT'].mean())
        filtered_data['FINAL LEAKAGE AMOUNT'] = filtered_data['FINAL LEAKAGE AMOUNT'].fillna(filtered_data['FINAL LEAKAGE AMOUNT'].mean())
        filtered_data['POTENTIAL LEAKAGE AMOUNT'] = filtered_data['POTENTIAL LEAKAGE AMOUNT'].fillna(filtered_data['POTENTIAL LEAKAGE AMOUNT'].mean())
        # filtered_data['Leakage Rate %'] = filtered_data['FINAL LEAKAGE AMOUNT'] / filtered_data.apply(
        #     lambda row: max(row['FINAL LEAKAGE AMOUNT'] - row['POTENTIAL LEAKAGE AMOUNT'], 1), axis=1
        # )

        filtered_data['FINAL LEAKAGE AMOUNT'] = filtered_data['FINAL LEAKAGE AMOUNT'].astype(float)
        filtered_data['POTENTIAL LEAKAGE AMOUNT'] = filtered_data['POTENTIAL LEAKAGE AMOUNT'].astype(float)
        
        # Calculate the difference and handle potential issues
        filtered_data['DIFFERENCE'] = filtered_data['FINAL LEAKAGE AMOUNT'] - filtered_data['POTENTIAL LEAKAGE AMOUNT']
        filtered_data['DIFFERENCE'] = filtered_data['DIFFERENCE'].apply(lambda x: max(x, 1))
        
        # Calculate Leakage Rate %
        filtered_data['Leakage Rate %'] = filtered_data['FINAL LEAKAGE AMOUNT'] / filtered_data['DIFFERENCE']
        # print("Generating graph")
        # Generate the graph using Plotly
        fig = px.line(filtered_data, x='CREATED DATE', y='Leakage Rate %', title='Leakage Rate Trend %')
        fig_json = fig.to_json()
        # Save the graph to a bytes buffer
        # buf = io.BytesIO()
        # fig.write_image(buf, format='png')
        # buf.seek(0)
        # graph_url = base64.b64encode(buf.read()).decode('utf-8')
        # buf.close()
        # print("Graph generated")
        return JsonResponse({'graph': fig_json})

def get_file_review_data(request):
    data_claim = pd.read_csv("C:/Users/abhishek221057/Downloads/claimauditable_1aug_31aug_seq10.csv", low_memory=False)
    data_claim = data_claim[['CLAIM ID', 'FINAL LOB', 'AUDIT DATE', 'OVERALL SCORE','PARAMETER SCORE AI']]

    min_date, max_date = data_claim['AUDIT DATE'].min(), data_claim['AUDIT DATE'].max()
    start_date = request.GET.get('start_date', min_date)
    end_date = request.GET.get('end_date', max_date)
    
    filtered_data = data_claim[data_claim['AUDIT DATE'].between(start_date, end_date)]

    line_of_business = request.GET.getlist('line_of_business', [])
    if line_of_business:
        filtered_data = filtered_data[filtered_data['FINAL LOB'].isin(line_of_business)]

     # Calculate File Review Score %
    def calculate_file_review_score(group):
        total_overall_score = group['OVERALL SCORE'].sum()
        total_score_ai_met = group[group['PARAMETER SCORE AI'].lower() == 'met']['OVERALL SCORE'].sum()
        if total_overall_score == 0:
            return 0
        return total_score_ai_met / total_overall_score

    file_review_score = (
        filtered_data.groupby('AUDIT DATE')
        .apply(calculate_file_review_score)
        .reset_index(drop=True)
        .reset_index()
    )
    print(file_review_score)
    file_review_score.columns = ['audit_date', 'File Review Score %']
    # Generate the graph using Plotly
    fig = px.line(file_review_score, x='audit_date', y='File Review Score %', title='File Review Score Trend %')
    fig_json = fig.to_json()
    
    return JsonResponse({'graph': fig_json})