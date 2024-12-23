import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.io as pio
from datetime import datetime

def render_file_review_page():
    st.set_page_config(
        page_title="File Review",
        page_icon="📄",
        layout="wide"
    )

    # Inject custom CSS for smoother sidebar transitions
    st.markdown("""
        <style>
        .css-1d391kg {
            transition: margin-left 0.5s ease-in-out;
        }
        .css-1d391kg .css-1v3fvcr {
            transition: margin-left 0.5s ease-in-out;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("File Review")

    # Sidebar filters
    st.sidebar.header("Filters")
    # Date range selectors
    monitoring_date_range = st.sidebar.date_input(
        "Select Monitoring Date Range",
        value=(datetime(2024, 1, 1), datetime(2024, 12, 31)),
        min_value=datetime(2000, 1, 1),
        max_value=datetime(2030, 12, 31)
    )

    loss_date_range = st.sidebar.date_input(
        "Select Loss Date Range",
        value=(datetime(2024, 1, 1), datetime(2024, 12, 31)),
        min_value=datetime(2000, 1, 1),
        max_value=datetime(2030, 12, 31)
    )

    close_date_range = st.sidebar.date_input(
        "Select Close Date Range",
        value=(datetime(2024, 1, 1), datetime(2024, 12, 31)),
        min_value=datetime(2000, 1, 1),
        max_value=datetime(2030, 12, 31)
    )

    line_of_business = st.sidebar.selectbox("Line of Business", ['All', 'Motor', 'Property', 'Casualty', 'Travel'])
    subline_of_business = st.sidebar.selectbox("Subline of Business", ['All'])
    nature_of_loss = st.sidebar.selectbox("Nature of Loss", ['All', 'Collision', 'Fusion', 'Accidental Damage / Loss', 'Fire', 'Theft / Burglary', 'Glass (Windscreen)', 'Storm / Flood / Earthquake', 'Construction or Trade related', 'Damage', 'Theft', 'Impact', 'Glass', 'Assault', 'Water Damage - Non Storm', 'Fall - slip/trip', 'Theft / Vandalism', 'Breakdown', 'Vehicle Incident - Unregistered', 'Rent Default', 'Underground Services damage', 'Livestock', 'Vandalism / Malicious Damage', 'Crop', 'Fall - from height', 'Water', 'Impacts', 'Medical', 'Rescheduled', 'Financial Loss', 'Animals / Livestock', 'Luggage', 'Exposure to Silica', 'Manual Handling', 'Personal Accident or Illness', 'Contamination / Pollution', 'Mechanical Repair', 'Vehicle Incident - Registered', 'Product Defect', 'Cancellation', 'Delayed/Additional Expenses', 'Treatments', 'Spraydrift / Overspray'])
    cause_of_loss = st.sidebar.selectbox("Cause of Loss", ['All', 'Third Party Hit Insured in Rear', 'Water / Pool Pump', 'Hit Stationary Object', 'Accidentally Damaged - At Situation', 'Bushfire', 'Theft - At Situation', 'Hit Animal - No Recovery', 'Damaged Whilst Driving', 'Storm', 'Unsafe Manoeuvre by Insured', 'Burglary - Forced entry to building', 'Whilst Reversing', 'Insured Failed to Give Way', 'Lost - At Situation', 'Third Party Failed to Give Way', 'Faulty workmanship (of insured)', 'Damaged Whilst Parked', 'Lost - Away from Situation', 'Theft - Recovered', 'Vehicle', 'Runaway Vehicle', 'Unknown', 'Theft - Not Recovered', 'Hail', 'By Accident', 'Cyclone', 'Alleged or committed by customer', 'Burst Pipes', 'Lightning', 'Overflow of Apparatus', 'Surface condition', 'Insured Hit Third Party in Rear', 'Fire', 'Theft of keys', 'Machinery', 'Accidental', 'Air Conditioner', 'Vehicle - External', 'Earthquake', 'Refrigerator', 'Shower recess', 'Malicious Damage', 'Falling Tree or Branch', 'Work site practices', 'Attempted Theft', 'Tool of Trade / Working Tool', 'Flood', 'Electrical', 'Tenant Vacated Without Notice', 'Worker Error', 'Single Vehicle Accident', 'Notice to Leave / Eviction Notice Issued', 'Other Appliance', 'Other object', 'Other', 'Head On Collision', 'Vandalism / Malicious Damage', 'Spray Drift', 'Unsafe work practice', 'Third Party Property Damage (Other)', 'Storm Water Run-Off', 'Accidentally Damaged - Away from Situation', 'Theft from Vehicle - Personal Property', 'Deliberate / Intentional Act', 'Damage', 'Leaks or seepage', 'Hit by object', 'Illness', 'Fuel Contamination', 'Storm Surge', 'By Malicious Damage', 'Tripped on object/structure', 'Unforeseen Or Unforeseeable', 'By Impact', 'Loss of use', 'Vehicle - Internal', 'Legal Fees', 'Impact by Falling Object', 'Incident on premises', 'Third Party Property Damage (Loss of Load)', 'Hit Pedestrian / Cyclist', 'Lost/Stolen/Damaged/Delayed Luggage', 'Direct Exposure', 'Depth too shallow', 'Burglary - Forced entry to Situation', 'Electrocution', 'Theft from Vehicle - Parts / Accessories', 'Escape - other', 'Lifting / carrying', 'Burglary - Forced entry to outbuilding', 'Excavation / Digging / Drilling', 'Caused by tenant / occupier', 'Stairs / escalators', 'Theft - Away from Situation', 'Forced break & enter', 'Defective Product', 'Breakage / activation of sprinkler system', 'Faulty workmanship', 'Operation of Machinery / Equipment', 'Process - Other', 'Faulty plumbing installation / repairs', 'Driver error', 'Welding / Cutting / Grinding', 'By Earthquake', 'Incident off premises', 'Malicious Damage by Tenant', 'Failure / Breakdown', 'Arson', 'Spillage on floor', 'By Storm / Hail', 'Injury', 'Severe Weather Natural Disaster', 'Contamination', 'Whilst being towed / On trailer', 'Hit Animal - Recovery', 'Death', 'Sanitary fixture breakage', 'Lost - Overseas', 'Missed Connection', 'Owner occupier risk', 'Liquid / chemical spillage', 'Hidden Hazard', 'Supervision', 'Burst / failed pipes or fittings', 'Not fit for purpose', 'Storm & Tempest', 'By Design Fault/Installation', 'Lost control of animal', 'Animal', 'Explosion', 'Impact of stationary vehicle', 'Computer', 'State Of Emergency', 'Disease / illness', 'Failure to supervise', 'Spillage', 'Quality of work performed', 'Failure to locate', 'Escape - fencing maintenance', 'Straying Livestock', 'Accidentally Damaged - Goods in Transit', 'Physical reaction', 'Subsidence', 'Property owner exposure', 'Inadequate security', 'Faulty equipment', 'Weather conditions'])
    audit_status = st.sidebar.selectbox("Audit Status", ['All', 'Closed'])
    leakage_type = st.sidebar.selectbox("Leakage Type", ['All'])
    claim_state = st.sidebar.selectbox("Claim Status", ['All', 'Open', 'Closed'])
    claim_consultant = st.sidebar.text_input("Claim Consultant")
    team = st.sidebar.text_input("Team")
    brand = st.sidebar.text_input("Brand")
    parameter_category = st.sidebar.text_input("Parameter Category")
    parameter_name = st.sidebar.text_input("Parameter Name")
    quality_auditor = st.sidebar.text_input("Quality Auditor")

    # Default filter values
    default_params = {
        'line_of_business': 'All',
        'subline_of_business': 'All',
        'nature_of_loss': 'All',
        'cause_of_loss': 'All',
        'audit_status': 'All',
        'leakage_type': 'All',
        'claim_state': 'All',
        'claim_consultant': '',
        'team': '',
        'brand': '',
        'parameter_category': '',
        'parameter_name': '',
        'quality_auditor': '',
        'monitoring_start_date': monitoring_date_range[0].strftime('%Y-%m-%d'),
        'monitoring_end_date': monitoring_date_range[1].strftime('%Y-%m-%d'),
        'loss_start_date': loss_date_range[0].strftime('%Y-%m-%d'),
        'loss_end_date': loss_date_range[1].strftime('%Y-%m-%d'),
        'close_start_date': close_date_range[0].strftime('%Y-%m-%d'),
        'close_end_date': close_date_range[1].strftime('%Y-%m-%d')
    }

    # Fetch data with default filters when the app starts
    response = requests.get("http://localhost:8000/backend_app/generate_graphs", params=default_params)
    
    if response.status_code == 200:
        data = response.json()
        bar_line_graph_json = data.get('bar_line_graph')
        pie_chart_json = data.get('pie_chart')
        treemap_json = data.get('treemap')
        bar_graph_json = data.get('bar_graph')
        param_bar_graph_json = data.get('param_bar_graph')
        com_treemap_json = data.get('com_treemap')

        # Display the calculated values in a row
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Claims Monitored Count", data.get('claims_monitored_count'))
        col2.metric("Total Opportunities Identified", data.get('total_opportunities_identified'))
        col3.metric("Total Errors Identified", data.get('total_errors_identified'))
        col4.metric("File Review Score", data.get('file_review_score'))

        if bar_line_graph_json:
            bar_line_fig = pio.from_json(bar_line_graph_json)
            st.plotly_chart(bar_line_fig)

        if pie_chart_json:
            pie_fig = pio.from_json(pie_chart_json)
            st.plotly_chart(pie_fig)

        if treemap_json:
            treemap_fig = pio.from_json(treemap_json)
            st.plotly_chart(treemap_fig)

        if bar_graph_json:
            bar_fig = pio.from_json(bar_graph_json)
            st.plotly_chart(bar_fig)

        if param_bar_graph_json:
            param_bar_fig = pio.from_json(param_bar_graph_json)
            st.plotly_chart(param_bar_fig)

        if com_treemap_json:
            com_treemap = pio.from_json(com_treemap_json)
            st.plotly_chart(com_treemap)
    else:
        st.write("Error fetching data")

    # Button to apply filters
    if st.sidebar.button("Apply Filters"):
        params = {
            'line_of_business': line_of_business,
            'subline_of_business': subline_of_business,
            'nature_of_loss': nature_of_loss,
            'cause_of_loss': cause_of_loss,
            'audit_status': audit_status,
            'leakage_type': leakage_type,
            'claim_state': claim_state,
            'claim_consultant': claim_consultant,
            'team': team,
            'brand': brand,
            'parameter_category': parameter_category,
            'parameter_name': parameter_name,
            'quality_auditor': quality_auditor,
            'monitoring_start_date': monitoring_date_range[0].strftime('%Y-%m-%d'),
            'monitoring_end_date': monitoring_date_range[1].strftime('%Y-%m-%d'),
            'loss_start_date': loss_date_range[0].strftime('%Y-%m-%d'),
            'loss_end_date': loss_date_range[1].strftime('%Y-%m-%d'),
            'close_start_date': close_date_range[0].strftime('%Y-%m-%d'),
            'close_end_date': close_date_range[1].strftime('%Y-%m-%d')
        }
        
        response = requests.get("http://localhost:8000/backend_app/generate_graphs", params=params)
        
        if response.status_code == 200:
            data = response.json()
            bar_line_graph_json = data.get('bar_line_graph')
            pie_chart_json = data.get('pie_chart')
            treemap_json = data.get('treemap')
            bar_graph_json = data.get('bar_graph')
            param_bar_graph_json = data.get('param_bar_graph')
            com_treemap_json = data.get('com_treemap')

            # Display the calculated values in a row
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Claims Monitored Count", data.get('claims_monitored_count'))
            col2.metric("Total Opportunities Identified", data.get('total_opportunities_identified'))
            col3.metric("Total Errors Identified", data.get('total_errors_identified'))
            col4.metric("File Review Score", data.get('file_review_score'))

            if bar_line_graph_json:
                bar_line_fig = pio.from_json(bar_line_graph_json)
                st.plotly_chart(bar_line_fig)

            if pie_chart_json:
                pie_fig = pio.from_json(pie_chart_json)
                st.plotly_chart(pie_fig)

            if treemap_json:
                treemap_fig = pio.from_json(treemap_json)
                st.plotly_chart(treemap_fig)

            if bar_graph_json:
                bar_fig = pio.from_json(bar_graph_json)
                st.plotly_chart(bar_fig)

            if param_bar_graph_json:
                param_bar_fig = pio.from_json(param_bar_graph_json)
                st.plotly_chart(param_bar_fig)

            if com_treemap_json:
                com_treemap = pio.from_json(com_treemap_json)
                st.plotly_chart(com_treemap)
        else:
            st.write("Error fetching data")

# Call the function to render the page
render_file_review_page()