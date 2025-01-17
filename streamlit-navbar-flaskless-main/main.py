import streamlit as st
import utils as utl
from views import home, about, analysis, options, configuration
import pandas as pd
import io
from selenium import webdriver
from PIL import Image

st.set_page_config(layout="wide", page_title='Navbar sample')
# st.set_option('deprecation.showPyplotGlobalUse', False)
utl.inject_custom_css()
utl.navbar_component()

# Sidebar toggle button
if 'sidebar_visible' not in st.session_state:
    st.session_state.sidebar_visible = True

def toggle_sidebar():
    st.session_state.sidebar_visible = not st.session_state.sidebar_visible

# Add a small arrow button at the top for toggling the sidebar
st.markdown("""
    <style>
    .toggle-button {
        position: fixed;
        top: 10px;
        left: 10px;
        z-index: 1001;
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 5px 10px;
        cursor: pointer;
        font-size: 16px;
        border-radius: 5px;
    }
    </style>
    <button class="toggle-button" onclick="toggleSidebar()">&#x25C0;</button>
    <script>
    function toggleSidebar() {
        window.parent.postMessage({type: 'streamlit:toggleSidebar'}, '*');
    }
    </script>
""", unsafe_allow_html=True)

if st.session_state.sidebar_visible:
    # Create a sidebar for date inputs
    st.sidebar.title("Date Filters")
    start_date = st.sidebar.date_input("Start Date")
    end_date = st.sidebar.date_input("End Date")

    # Display the selected dates in the main page
    st.write(f"Selected Start Date: {start_date}")
    st.write(f"Selected End Date: {end_date}")

# Function to generate a sample report
def generate_report():
    # Sample data for the report
    data = {
        "Date": pd.date_range(start=start_date, end=end_date, freq='D'),
        "Value": range((end_date - start_date).days + 1)
    }
    df = pd.DataFrame(data)
    return df

# Add a download button for the report
if st.button("Download Report"):
    report_df = generate_report()
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        report_df.to_excel(writer, index=False, sheet_name='Report')
        writer.save()
    st.download_button(
        label="Download Complete Report",
        data=buffer,
        file_name="complete_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Function to capture a long screenshot of the current page
def capture_long_screenshot():
    # Set up Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)

    # Open the Streamlit app
    driver.get("http://localhost:8501")

    # Get the total height of the page
    total_height = driver.execute_script("return document.body.scrollHeight")
    viewport_height = driver.execute_script("return window.innerHeight")
    total_width = driver.execute_script("return document.body.scrollWidth")

    # Initialize an empty image to stitch screenshots
    stitched_image = Image.new('RGB', (total_width, total_height))

    # Scroll and capture screenshots
    for i in range(0, total_height, viewport_height):
        driver.execute_script(f"window.scrollTo(0, {i});")
        screenshot = driver.get_screenshot_as_png()
        screenshot_image = Image.open(io.BytesIO(screenshot))

        # Calculate the position to paste the screenshot
        paste_position = (0, i)

        # Ensure the screenshot fits within the bounds of the base image
        if i + viewport_height > total_height:
            screenshot_image = screenshot_image.crop((0, 0, total_width, total_height - i))

        stitched_image.paste(screenshot_image, paste_position)

    driver.quit()

    # Save the stitched image
    buffer = io.BytesIO()
    stitched_image.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer

# Add a button to capture and download the long screenshot
if st.button("Download Page as Image"):
    screenshot_buffer = capture_long_screenshot()
    st.download_button(
        label="Download Page as Image",
        data=screenshot_buffer,
        file_name="page.png",
        mime="image/png"
    )

def navigation():
    route = utl.get_current_route()
    if route == "home":
        home.load_view()
    elif route == "about":
        about.load_view()
    elif route == "analysis":
        analysis.load_view()
    elif route == "options":
        options.load_view()
    elif route == "configuration":
        configuration.load_view()
    elif route is None:
        home.load_view()

navigation()