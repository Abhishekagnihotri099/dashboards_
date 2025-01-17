import streamlit as st

def page1():
    st.write("This is the home page")

def page2():
    st.write("This is the filter page")

def page3():
    st.write("This is the settings page")

def page4():
    st.write("This is the map page")

pages = {
    "Home": page1,
    "Filter": page2,
    "Settings": page3,
    "Map": page4
}

st.set_page_config(layout="wide")

# Create a top navigation bar
st.markdown("""
    <style>
    .topnav {
        overflow: hidden;
        background-color: #333;
        position: fixed;
        top: 0;
        width: 100%;
        z-index: 1000;
    }

    .topnav a {
        float: left;
        display: block;
        color: #f2f2f2;
        text-align: center;
        padding: 14px 16px;
        text-decoration: none;
        font-size: 17px;
    }

    .topnav a:hover {
        background-color: #ddd;
        color: black;
    }

    .topnav a.active {
        background-color: #4CAF50;
        color: white;
    }

    .content {
        padding: 60px 10px;
    }
    </style>
    <div class="topnav">
        <a href="?page=Home" class="active">Home</a>
        <a href="?page=Filter">Filter</a>
        <a href="?page=Settings">Settings</a>
        <a href="?page=Map">Map</a>
    </div>
    <div class="content">
""", unsafe_allow_html=True)

# Create a sidebar for additional elements
st.sidebar.title("Date Filters")
start_date = st.sidebar.date_input("Start Date")
end_date = st.sidebar.date_input("End Date")

# Display the selected dates in the main page
st.write(f"Selected Start Date: {start_date}")
st.write(f"Selected End Date: {end_date}")

# Determine the current page based on the URL query parameter
current_page = st.query_params.get("page", ["Home"])[0]

# Run the selected page
if current_page in pages:
    pages[current_page]()
else:
    st.write("Page not found")

st.markdown("</div>", unsafe_allow_html=True)