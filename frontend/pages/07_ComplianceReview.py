import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime, timedelta
import json

def render_compliance_review_page():
    st.title("Compliance Review Dashboard")

    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Date filters
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input("End Date", datetime.now())

    # Multi-select filters
    lob = st.sidebar.multiselect(
        "Line of Business",
        ["Motor", "Home", "Commercial"],
        default=["Motor"]
    )
    
    claim_status = st.sidebar.multiselect(
        "Claim Status",
        ["Open", "Closed", "Pending"],
        default=["Open"]
    )

    # Apply filters button
    if st.sidebar.button("Apply Filters"):
        # Prepare filter parameters
        params = {
            'monitoring_date_start': start_date.strftime('%Y-%m-%d'),
            'monitoring_date_end': end_date.strftime('%Y-%m-%d'),
            'line_of_business': lob,
            'claim_status': claim_status
        }

        # API call
        response = requests.get(
            'http://localhost:8000/api/compliance-review/filter/',
            params=params
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Display metrics in columns
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Claims Monitored", data['metrics']['claims_monitored'])
            with col2:
                st.metric("Compliance Opportunities", data['metrics']['claims_with_compliance_opportunity'])
            with col3:
                st.metric("Opportunity %", f"{data['metrics']['compliance_opportunity_percentage']:.2f}%")

            # Display graphs
            st.subheader("Compliance Opportunities Trend")
            st.plotly_chart(json.loads(data['graphs']['compliance_opportunities_trend']))
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Opportunities by Category")
                st.plotly_chart(json.loads(data['graphs']['compliance_opportunities_by_category']))
            with col2:
                st.subheader("Opportunities by Consultant")
                st.plotly_chart(json.loads(data['graphs']['compliance_opportunities_by_consultant']))

            st.subheader("Opportunities by Parameter")
            st.plotly_chart(json.loads(data['graphs']['compliance_opportunities_by_parameter']))

            st.subheader("Error % by Consultant")
            st.plotly_chart(json.loads(data['graphs']['error_by_consultant']))

            st.subheader("Opportunities by Compliance Reasons")
            st.plotly_chart(json.loads(data['graphs']['claim_opportunity_by_compliance_reasons']))

            # Display data table
            st.subheader("Detailed Data")
            st.dataframe(pd.DataFrame(data['table_data']))
        else:
            st.error("Error fetching data from API")

if __name__ == "__main__":
    render_compliance_review_page()