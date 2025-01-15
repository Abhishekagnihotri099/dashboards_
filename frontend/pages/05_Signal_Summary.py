import streamlit as st
import pandas as pd
import requests

def signal_summary_page():
    st.set_page_config(page_title="Signal Summary", page_icon="📊", layout="wide")

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
            font-size: 1.0rem; /* Reduced font size */
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
    st.markdown("<h1 style='color: var(--primary-color); margin-bottom: 2rem; padding-bottom: 0.5rem; border-bottom: 2px solid var(--primary-color);'>Signal Summary</h1>", unsafe_allow_html=True)
    # Backend API URL
    API_URL = "http://localhost:8000/sds_signal_summary/filter_signal_summary"

    # Streamlit app
    # st.title("SDS Signal Summary")

    # Sidebar filters
    st.sidebar.header("Filters")
    # Date filters
    signal_generated_date_range = st.sidebar.date_input("Signal Generated Date", [pd.to_datetime('2024-01-01'), pd.to_datetime('2024-12-31')], key='signal_generated_date_range')
    signal_assigned_date_range = st.sidebar.date_input("Signal Assigned Date", [pd.to_datetime('2024-01-01'), pd.to_datetime('2024-12-31')], key='signal_assigned_date_range')
    signal_closed_date_range = st.sidebar.date_input("Signal Closed Date", [pd.to_datetime('2024-01-01'), pd.to_datetime('2024-12-31')], key='signal_closed_date_range')

    # Line of Business filter
    line_of_business_options = ['All', 'Motor', 'Property', 'Travel', 'Casualty']
    line_of_business = st.sidebar.multiselect('Line of Business', options=line_of_business_options, default=['All'])

    if 'All' in line_of_business:
        line_of_business = line_of_business_options[1:]

    # Parameter Name filter
    parameter_name = st.sidebar.text_input("Parameter Name")

    # Fetch data from backend API
    params = {
        'signal_generated_start_date': signal_generated_date_range[0].strftime('%Y-%m-%d'),
        'signal_generated_end_date': signal_generated_date_range[1].strftime('%Y-%m-%d'),
        'signal_assigned_start_date': signal_assigned_date_range[0].strftime('%Y-%m-%d'),
        'signal_assigned_end_date': signal_assigned_date_range[1].strftime('%Y-%m-%d'),
        'signal_closed_start_date': signal_closed_date_range[0].strftime('%Y-%m-%d'),
        'signal_closed_end_date': signal_closed_date_range[1].strftime('%Y-%m-%d'),
        "line_of_business": line_of_business,
        "parameter_name": parameter_name,
    }

    response = requests.get(API_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        metrics = data.get('metrics', {})
        table_data = data.get('table_data', [])

        # Display metrics
        # st.header("Metrics")
        metric_keys = list(metrics.keys())
        metric_values = list(metrics.values())

        # Display first row of metrics
        cols = st.columns(6)
        for i in range(6):
            with cols[i]:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">{metric_keys[i].replace('_', ' ').title()}</div>
                    <div class="metric-value">{metric_values[i]}</div>
                </div>
                """, unsafe_allow_html=True)

        # Add space between rows
        st.markdown("<br><br>", unsafe_allow_html=True)

        # Display second row of metrics
        cols = st.columns(6)
        for i in range(6, len(metric_keys)):
            with cols[i - 6]:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">{metric_keys[i].replace('_', ' ').title()}</div>
                    <div class="metric-value">{metric_values[i]}</div>
                </div>
                """, unsafe_allow_html=True)

        # Display table data
        st.header("Table Data")
        df_table = pd.DataFrame(table_data)
        st.dataframe(df_table)
    else:
        st.error("Failed to fetch data from the API.")

# Run the Streamlit app
if __name__ == "__main__":
    signal_summary_page()