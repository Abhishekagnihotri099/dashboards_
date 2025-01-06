import streamlit as st
import requests
import pandas as pd
import plotly.io as pio
from datetime import datetime

def render_ai_accuracy_page():
    st.set_page_config(page_title="AI Accuracy", page_icon="🎯", layout="wide")

    # Custom CSS for metric cards
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

    st.title("🤖 AI Accuracy Dashboard")

    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Date range filters
    ai_monitoring_range = st.sidebar.date_input(
        "AI Monitoring Date Range",
        value=(datetime(2024, 1, 1), datetime(2024, 12, 31)),
        min_value=datetime(2000, 1, 1),
        max_value=datetime(2030, 12, 31)
    )
    
    manual_monitoring_range = st.sidebar.date_input(
        "Manual Monitoring Date Range",
        value=(datetime(2024, 1, 1), datetime(2024, 12, 31)),
        min_value=datetime(2000, 1, 1),
        max_value=datetime(2030, 12, 31)
    )

    # Other filters
    parameter_name = st.sidebar.selectbox("Parameter Name", ['All'])
    leakage_category = st.sidebar.selectbox("Leakage Category", ['All'])
    line_of_business = st.sidebar.selectbox("Line of Business", ['All'])
    audited_by = st.sidebar.text_input("Audited By")
    parameter_score_ai = st.sidebar.selectbox("AI Output", ['All', 'Met', 'Not Met', 'NA'])

    if st.sidebar.button("Apply Filters", type="primary"):
        params = {
            'ai_monitoring_start_date': ai_monitoring_range[0].strftime('%Y-%m-%d'),
            'ai_monitoring_end_date': ai_monitoring_range[1].strftime('%Y-%m-%d'),
            'manual_monitoring_start_date': manual_monitoring_range[0].strftime('%Y-%m-%d'),
            'manual_monitoring_end_date': manual_monitoring_range[1].strftime('%Y-%m-%d'),
            'parameter_name': parameter_name,
            'leakage_category': leakage_category,
            'line_of_business': line_of_business,
            'audited_by': audited_by,
            'parameter_score_ai': parameter_score_ai
        }

        response = requests.get("http://localhost:8000/sds_ai_accuracy/", params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("""
                    <div class="metric-card">
                        <h3>Claims Monitored by AI</h3>
                        <div class="metric-value">{:,}</div>
                    </div>
                """.format(data['claims_monitored_by_ai']), unsafe_allow_html=True)
                
            with col2:
                st.markdown("""
                    <div class="metric-card">
                        <h3>Claims Monitored Manually</h3>
                        <div class="metric-value">{:,}</div>
                    </div>
                """.format(data['claims_monitored_manually']), unsafe_allow_html=True)
                
            with col3:
                st.markdown("""
                    <div class="metric-card">
                        <h3>% Claims Monitored Manually</h3>
                        <div class="metric-value">{:.2f}%</div>
                    </div>
                """.format(data['percent_claims_monitored_manually']), unsafe_allow_html=True)
                
            with col4:
                st.markdown("""
                    <div class="metric-card">
                        <h3>AI Accuracy</h3>
                        <div class="metric-value">{:.2f}%</div>
                    </div>
                """.format(data['ai_accuracy']), unsafe_allow_html=True)

            # Display yearly trend chart
            st.subheader("Yearly AI Accuracy Trend")
            yearly_chart = pio.from_json(data['yearly_accuracy_trend'])
            st.plotly_chart(yearly_chart, use_container_width=True)
            
            # Display monthly parameter table
            st.subheader("Monthly Parameter-wise Accuracy")
            monthly_df = pd.DataFrame(data['monthly_parameter_accuracy'])
            
            # Add download button
            csv = monthly_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Monthly Data",
                data=csv,
                file_name="monthly_accuracy.csv",
                mime="text/csv"
            )
            
            # Display table with formatting
            st.dataframe(
                monthly_df,
                hide_index=True,
                column_config={
                    col: st.column_config.NumberColumn(
                        format="%.2f%%"
                    ) for col in monthly_df.columns if col != 'parameter_name'
                },
                use_container_width=True
            )
        else:
            st.error("Error fetching data from backend")

if __name__ == "__main__":
    render_ai_accuracy_page()