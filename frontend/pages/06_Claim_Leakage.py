import streamlit as st
import requests
import json
import plotly.graph_objects as go
from datetime import datetime, timedelta

def load_claim_leakage_dashboard():
    st.title("Claim Leakage Dashboard")

    # Sidebar filters
    with st.sidebar:
        st.header("Filters")
        
        # Date filters
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
        with col2:
            end_date = st.date_input("End Date", datetime.now())

        # Other filters
        lob = st.multiselect("Line of Business", ["Motor", "Home", "Commercial"])
        consultant = st.multiselect("Claim Consultant", ["Consultant1", "Consultant2"])
        
        apply_filters = st.button("Apply Filters")

    # Main content area - outside sidebar
    if apply_filters:
        params = {
            'monitoring_date_start': start_date.strftime('%Y-%m-%d'),
            'monitoring_date_end': end_date.strftime('%Y-%m-%d'),
            # 'line_of_business': lob,
            # 'claim_consultant': consultant
        }
        
        response = requests.get('http://localhost:8000/sds_claim_leakage/generate_graphs', params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # Create tabs in main area
            tab1, tab2, tab3 = st.tabs(["Overview", "Leakage Analysis", "AI Performance"])
            
            with tab1:
                # Overview metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Claims", "1000")
                with col2:
                    st.metric("Total Leakage", "$500K")
                with col3:
                    st.metric("Opportunities", "150")
                
                # Leakage trend graph
                st.subheader("Leakage Trend")
                fig = go.Figure(json.loads(data['leakage_trend']))
                st.plotly_chart(fig)
                
                # Opportunity trend
                st.subheader("Opportunity Identification Trend")
                fig2 = go.Figure(json.loads(data['opportunity_trend']))
                st.plotly_chart(fig2)

            with tab2:
                col1, col2 = st.columns(2)
                with col1:
                    # Leakage by category pie
                    fig3 = go.Figure(json.loads(data['leakage_category_pie']))
                    st.plotly_chart(fig3)
                
                with col2:
                    # Leakage hierarchy
                    fig4 = go.Figure(json.loads(data['leakage_hierarchy']))
                    st.plotly_chart(fig4)
                
                # Consultant treemap
                fig5 = go.Figure(json.loads(data['consultant_treemap']))
                st.plotly_chart(fig5)
                
                # Parameter leakage
                fig6 = go.Figure(json.loads(data['parameter_leakage']))
                st.plotly_chart(fig6)

            with tab3:
                # AI Performance graphs
                st.subheader("AI Performance Analysis")
                fig10 = go.Figure(json.loads(data['consultant_ai_performance']))
                st.plotly_chart(fig10)
                
                # Sankey diagram
                st.subheader("Leakage Flow Analysis")
                fig11 = go.Figure(json.loads(data['leakage_flow_sankey']))
                st.plotly_chart(fig11)
        
        else:
            st.error("Error fetching data from API")

if __name__ == "__main__":
    load_claim_leakage_dashboard()