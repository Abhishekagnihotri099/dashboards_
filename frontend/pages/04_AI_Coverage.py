import streamlit as st
import requests
import pandas as pd
import plotly.io as pio
from datetime import datetime

def render_ai_coverage_page():
    # Performance optimization: Set page config with minimal layout
    st.set_page_config(
        page_title="AI Coverage",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Modern PowerBI-like styling
    st.markdown("""
        <style>
        /* Main theme colors */
        :root {
            --primary-color: #0078D4;
            --background-color: #F5F5F5;
            --card-background: #FFFFFF;
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background-color: var(--card-background);
        }
        
        /* Metric cards */
        .metric-card {
            background-color: var(--card-background);
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
            transition: transform 0.2s ease;
            height: 150px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        .metric-label {
            font-size: 0.9rem;
            color: #666666;
            margin-bottom: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: 600;
            color: var(--primary-color);
            margin-bottom: 0.5rem;
        }

        /* Table styling */
        .stDataFrame {
            background-color: var(--card-background);
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        }

        /* Chart container */
        .chart-container {
            background-color: var(--card-background);
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
            margin: 1rem 0;
        }

        /* Download button */
        .stDownloadButton {
            background-color: var(--primary-color) !important;
            color: white !important;
            padding: 0.5rem 1rem !important;
            border-radius: 4px !important;
            border: none !important;
            transition: background-color 0.2s ease !important;
        }

        .stDownloadButton:hover {
            background-color: #005a9e !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Page header with subtle separator
    st.markdown("<h1 style='color: #0078D4; margin-bottom: 2rem; padding-bottom: 0.5rem; border-bottom: 2px solid #0078D4;'>📊 AI Coverage Dashboard</h1>", unsafe_allow_html=True)

    # Sidebar optimization
    with st.sidebar:
        st.markdown("<h2 style='color: #0078D4;'>Filters</h2>", unsafe_allow_html=True)
        
        ai_monitoring_range = st.date_input(
            "AI Monitoring Date Range",
            value=(datetime(2024, 1, 1), datetime(2024, 12, 31)),
            min_value=datetime(2000, 1, 1),
            max_value=datetime(2030, 12, 31)
        )

        parameter_name = st.selectbox("Parameter Name", ['All'])
        leakage_category = st.selectbox("Leakage Category", ['All'])
        line_of_business = st.selectbox("Line of Business", ['All'])
        parameter_score_ai = st.selectbox("AI Output", ['All', 'Met', 'Not Met', 'NA'])

        st.markdown("<br>", unsafe_allow_html=True)
        apply_button = st.button("Apply Filters", type="primary", use_container_width=True)

    if apply_button:
        # Loading state
        with st.spinner('Fetching data...'):
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
                
                # Metrics row with equal-sized cards
                col1, col2, col3 = st.columns(3)
                
                metrics = [
                    ("Total Claims", data['metrics']['total_claims'], ""),
                    ("Claims Monitored", data['metrics']['claims_monitored_successfully'], ""),
                    ("Coverage", data['metrics']['coverage_percentage'], "%")
                ]

                for col, (label, value, suffix) in zip([col1, col2, col3], metrics):
                    with col:
                        st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-label">{label}</div>
                                <div class="metric-value">{value:,.2f}{suffix}</div>
                            </div>
                        """, unsafe_allow_html=True)

                # Coverage trend chart
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                st.subheader("AI Coverage Trend")
                coverage_chart = pio.from_json(data['coverage_graph'])
                st.plotly_chart(coverage_chart, use_container_width=True, theme="streamlit")
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Parameter coverage analysis
                st.subheader("Parameter Coverage Analysis")
                param_df = pd.DataFrame(data['parameter_coverage'])
                
                # Download button with improved styling
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    csv = param_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Parameter Coverage Data",
                        data=csv,
                        file_name="parameter_coverage.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                # Enhanced table display
                st.dataframe(
                    param_df,
                    hide_index=True,
                    column_config={
                        'parameter_name': st.column_config.TextColumn('Parameter Name', width='large'),
                        'opportunities': st.column_config.NumberColumn('Opportunities', format="%d"),
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