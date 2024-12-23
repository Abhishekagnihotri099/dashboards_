import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.io as pio

st.set_page_config(page_title="Homepage", page_icon="🌟", layout="wide")

st.title("Home")

# Streamlit Sidebar for Filter Options
st.sidebar.header("Filter Options")

# Radio options for selection
radio_opt = ["Leakage Rate Trend %", "File Review Score Trend %"]
selected_opt = st.radio(label="Choose the view", options=radio_opt)

if radio_opt.index(selected_opt)==0:
    date_range = st.sidebar.date_input("Monitoring Date (Leakage)", [pd.to_datetime('2024-01-01'), pd.to_datetime('2024-12-31')], key='date_range')
    start_date, end_date = date_range[0], date_range[1]
    line_of_business_options = ['All', 'Motor', 'Property']
    line_of_business = st.sidebar.multiselect('Line of Business (Leakage)', options=line_of_business_options, default=['All'])

    if 'All' in line_of_business:
        line_of_business = line_of_business_options[1:]
    # Define API endpoint for filtered data
    API_URL = "http://localhost:8000/backened/api/filtered-data-leakage/"

    # Fetch filtered data from Django API
    params = {
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'line_of_business': line_of_business
    }

    response = requests.get(API_URL, params=params)
    if response.status_code == 200:
        graph_data = response.json()
        fig = pio.from_json(graph_data['graph'])
        # Display the graph
        st.plotly_chart(fig)
    else:
        st.error("Failed to fetch data from the API.")

elif radio_opt.index(selected_opt)==1:
    date_range = st.sidebar.date_input("Monitoring Date (File Review)", [pd.to_datetime('2024-01-01'), pd.to_datetime('2024-12-31')], key='date_range')
    start_date, end_date = date_range[0], date_range[1]
    line_of_business_options = ['All', 'Motor', 'Property']
    line_of_business = st.sidebar.multiselect('Line of Business (File Review)', options=line_of_business_options, default=['All'])

    if 'All' in line_of_business:
        line_of_business = line_of_business_options[1:]

    API_URL = "http://localhost:8000/backened/api/filtered-data-filereview/"

    # Fetch filtered data from Django API
    params = {
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'line_of_business': line_of_business
    }

    response = requests.get(API_URL, params=params)
    if response.status_code == 200:
        graph_data = response.json()
        fig = pio.from_json(graph_data['graph'])
        # Display the graph
        st.plotly_chart(fig)
    else:
        st.error("Failed to fetch data from the API.")