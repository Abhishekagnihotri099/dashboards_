import streamlit as st
import requests
import pandas as pd
import plotly.io as pio
from datetime import datetime

def render_ai_coverage_page():
    st.set_page_config(page_title="AI Coverage", page_icon="📊", layout="wide")

    # Custom CSS
    st.markdown("""
        <style>
        .metric-card {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            color: #0366d6;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("📊 AI Coverage Dashboard")

    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Date range filter
    ai_monitoring_range = st.sidebar.date_input(
        "AI Monitoring Date Range",
        value=(datetime(2024, 1, 1), datetime(2024, 12, 31)),
        min_value=datetime(2000, 1, 1),
        max_value=datetime(2030, 12, 31)
    )

    # Other filters
    parameter_name = st.sidebar.selectbox("Parameter Name", ['All'])
    leakage_category = st.sidebar.selectbox("Leakage Category", ['All'])
    line_of_business = st.sidebar.selectbox("Line of Business", ['All'])
    parameter_score_ai = st.sidebar.selectbox("AI Output", ['All', 'Met', 'Not Met', 'NA'])

    if st.sidebar.button("Apply Filters", type="primary"):
        params = {
            'ai_monitoring_start_date': ai_monitoring_range[0].strftime('%Y-%m-%d'),
            'ai_monitoring_end_date': ai_monitoring_range[1].strftime('%Y-%m-%d'),
            'parameter_name': parameter_name,
            'leakage_category': leakage_category,
            'line_of_business': line_of_business,
            'parameter_score_ai': parameter_score_ai
        }

        response = requests.get("http://127.0.0.1:8000/sds_ai_coverage/ai_coverage_view", params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                    <div class="metric-card">
                        <h3>Total Claims</h3>
                        <div class="metric-value">{:,}</div>
                    </div>
                """.format(data['metrics']['total_claims']), unsafe_allow_html=True)
                
            with col2:
                st.markdown("""
                    <div class="metric-card">
                        <h3>Claims Monitored Successfully</h3>
                        <div class="metric-value">{:,}</div>
                    </div>
                """.format(data['metrics']['claims_monitored_successfully']), unsafe_allow_html=True)
                
            with col3:
                st.markdown("""
                    <div class="metric-card">
                        <h3>Coverage Percentage</h3>
                        <div class="metric-value">{:.2f}%</div>
                    </div>
                """.format(data['metrics']['coverage_percentage']), unsafe_allow_html=True)

            # Display coverage trend
            st.subheader("AI Coverage Trend")
            coverage_chart = pio.from_json(data['coverage_graph'])
            st.plotly_chart(coverage_chart, use_container_width=True)
            
            # Display parameter coverage table
            st.subheader("Parameter Coverage Analysis")
            param_df = pd.DataFrame(data['parameter_coverage'])
            
            # Add download button
            csv = param_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Parameter Coverage Data",
                data=csv,
                file_name="parameter_coverage.csv",
                mime="text/csv"
            )
            
            # Display table with formatting
            st.dataframe(
                param_df,
                hide_index=True,
                column_config={
                    'parameter_name': 'Parameter Name',
                    'opportunities': st.column_config.NumberColumn('Opportunities'),
                    'overall_coverage': st.column_config.NumberColumn(
                        'Overall Coverage %',
                        format="%.2f%%"
                    ),
                    **{col: st.column_config.NumberColumn(
                        f'{col} Coverage %',
                        format="%.2f%%"
                    ) for col in param_df.columns if '-' in str(col)}
                },
                use_container_width=True
            )
        else:
            st.error("Error fetching data from backend")

if __name__ == "__main__":
    render_ai_coverage_page()