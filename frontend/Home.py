import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.io as pio


def render_home_page():
    st.set_page_config(page_title="Homepage", page_icon="🌟", layout="wide")
     # Add these CSS rules to the existing style block
    st.markdown("""
        <style>
        /* Remove top padding and white space */
        .main > div {
            padding-top: 0rem;
        }
        
        /* Remove default header margin */
        .stApp header {
            background: none;
        }
        
        /* Adjust container spacing */
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            max-width: 100%;
        }
        
        /* Existing CSS rules... */
        :root {
            --primary-color: #0078D4;
            --secondary-color: #005A9E;
            --background-color: #F5F5F5;
            --card-background: #FFFFFF;
            --text-primary: #252525;
            --text-secondary: #666666;
        }
        
        /* Global styles */
        .stApp {
            background-color: var(--background-color);
        }
        
        /* Header */
        h1, h2, h3 {
            color: var(--primary-color);
            font-weight: 600;
        }
        
        /* Metric cards */
        .metric-card {
            background: var(--card-background);
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
            transition: transform 0.2s ease;
            height: 160px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        .metric-title {
            font-size: 0.9rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.5rem;
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: 600;
            color: var(--primary-color);
            margin-bottom: 0.5rem;
        }
        
        /* Progress bar */
        .progress-container {
            width: 100%;
            background-color: #E5E5E5;
            border-radius: 4px;
            margin-top: 0.5rem;
            overflow: hidden;
        }
        
        .progress-bar {
            height: 6px;
            background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
            border-radius: 4px;
            transition: width 0.5s ease-in-out;
        }
        
        /* Chart containers */
        .chart-container {
            background: var(--card-background);
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
            margin: 1rem 0;
            transition: transform 0.2s ease;
        }

        .chart-container:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        /* Sidebar */
        .css-1d391kg {
            background-color: var(--card-background);
            padding: 1rem;
        }
        
        /* Section dividers */
        .section-divider {
            margin: 2rem 0;
            border-bottom: 1px solid #E5E5E5;
        }
        
        /* Loading spinner */
        .stSpinner {
            border-color: var(--primary-color);
        }

        /* Add section title styling */
        h2 {
            margin: 2rem 0 1rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--primary-color);
            color: var(--primary-color);
            font-size: 1.5rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # PowerBI-like header
    st.markdown("<h1 style='color: var(--primary-color); margin-bottom: 2rem; padding-bottom: 0.5rem; border-bottom: 2px solid var(--primary-color);'>Home</h1>", unsafe_allow_html=True)

    # st.title("Home")

    # Streamlit Sidebar for Filter Options
    st.sidebar.header("Filter Options")

    # Radio options for selection
    radio_opt = ["Leakage Rate Trend %", "File Review Score Trend %"]
    selected_opt = st.radio(label="Choose the view", options=radio_opt)

    if radio_opt.index(selected_opt)==0:
        date_range = st.sidebar.date_input("Monitoring Date (Leakage)", [pd.to_datetime('2024-01-01'), pd.to_datetime('2024-12-31')], key='date_range')
        start_date, end_date = date_range[0], date_range[1]
        line_of_business_options = ['All', 'Motor', 'Property', 'Travel', 'Casulty']
        line_of_business = st.sidebar.multiselect('Line of Business (Leakage)', options=line_of_business_options, default=['All'])

        if 'All' in line_of_business:
            line_of_business = line_of_business_options[1:]
        # Define API endpoint for filtered data
        API_URL = "http://localhost:8000/SDS_Home/filter_data_home_page1"

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
        line_of_business_options = ['All', 'Motor', 'Property', 'Travel', 'Casulty']
        line_of_business = st.sidebar.multiselect('Line of Business (File Review)', options=line_of_business_options, default=['All'])

        if 'All' in line_of_business:
            line_of_business = line_of_business_options[1:]

        API_URL = "http://localhost:8000/SDS_Home/filter_data_home_page2"

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

render_home_page()