import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date

def compliance_review_page():
    # Set the title of the Streamlit app
    st.title("Compliance Review Dashboard")

    # Define the API endpoint
    api_endpoint = "http://localhost:8000/sds_compliance_review/filter_compliance_review/"

    # Create a sidebar for filters
    st.sidebar.header("Filters")

    # Define filter inputs with default dates
    default_start_date = date(2024, 1, 1)
    default_end_date = date(2024, 12, 31)

    # Define filter inputs
    monitoring_date_start = st.sidebar.date_input("Monitoring Date Start", default_start_date)
    monitoring_date_end = st.sidebar.date_input("Monitoring Date End", default_end_date)
    loss_date_start = st.sidebar.date_input("Loss Date Start", default_start_date)
    loss_date_end = st.sidebar.date_input("Loss Date End", default_end_date)
    claim_closed_date_start = st.sidebar.date_input("Claim Closed Date Start", default_start_date)
    claim_closed_date_end = st.sidebar.date_input("Claim Closed Date End", default_end_date)
    line_of_business = st.sidebar.multiselect("Line of Business", [])
    sub_line_of_business = st.sidebar.multiselect("Sub Line of Business", [])
    nature_of_loss = st.sidebar.multiselect("Nature of Loss", [])
    cause_of_loss = st.sidebar.multiselect("Cause of Loss", [])
    claim_status = st.sidebar.multiselect("Claim Status", [])
    claim_state = st.sidebar.multiselect("Claim State", [])
    claim_consultant = st.sidebar.multiselect("Claim Consultant", [])
    team = st.sidebar.multiselect("Team", [])
    accurate_signal = st.sidebar.selectbox("Accurate Signal", ["Yes", "No"])
    brand = st.sidebar.multiselect("Brand", [])
    compliance_category = st.sidebar.multiselect("Compliance Category", [])
    parameter_name = st.sidebar.text_input("Parameter Name")
    signal_status = st.sidebar.selectbox("Signal Status", ["Open", "Closed", "Pending"])
    manual_review = st.sidebar.selectbox("Manual Review", ["Yes", "No"])
    signal_reviewed_by = st.sidebar.text_input("Signal Reviewed By")

    # Create a button to apply filters
    # if st.sidebar.button("Apply Filters"):
        # Build the query parameters
    params = {
        "monitoring_date_start": monitoring_date_start.strftime('%Y-%m-%d'),
        "monitoring_date_end": monitoring_date_end.strftime('%Y-%m-%d'),
        "loss_date_start": loss_date_start.strftime('%Y-%m-%d'),
        "loss_date_end": loss_date_end.strftime('%Y-%m-%d'),
        "claim_closed_date_start": claim_closed_date_start.strftime('%Y-%m-%d'),
        "claim_closed_date_end": claim_closed_date_end.strftime('%Y-%m-%d'),
        "line_of_business": line_of_business,
        "sub_line_of_business": sub_line_of_business,
        "nature_of_loss": nature_of_loss,
        "cause_of_loss": cause_of_loss,
        "claim_status": claim_status,
        "claim_state": claim_state,
        "claim_consultant": claim_consultant,
        "team": team,
        "accurate_signal": accurate_signal,
        "brand": brand,
        "compliance_category": compliance_category,
        "parameter_name": parameter_name,
        "signal_status": signal_status,
        "manual_review": manual_review,
        "signal_reviewed_by": signal_reviewed_by,
    }

    # Fetch data from the API
    try:
        response = requests.get(api_endpoint, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")
        st.stop()
    except requests.exceptions.JSONDecodeError:
        st.error("Failed to decode JSON response from the API.")
        st.stop()

    # Display metrics
    st.header("Metrics")
    metrics = data["metrics"]
    col1, col2, col3 = st.columns(3)
    col1.metric("Claims Monitored", metrics["claims_monitored"])
    col2.metric("Claims with Compliance Opportunity", metrics["claims_with_compliance_opportunity"])
    col3.metric("Compliance Opportunity Percentage", f"{metrics['compliance_opportunity_percentage']}%")

    # Display graphs
    # st.header("Graphs")
    graphs = data["graphs"]
    for graph_title, graph_json in graphs.items():
        st.subheader(graph_title.replace("_", " ").title())
        fig = go.Figure(graph_json)
        st.plotly_chart(fig)

    # Display table data
    st.header("Table Data")
    table_data = pd.DataFrame(data["table_data"])
    st.dataframe(table_data)

# Run the Streamlit app
if __name__ == "__main__":
    compliance_review_page()