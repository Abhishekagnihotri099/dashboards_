import streamlit as st

# Simulate a top navigation bar with a selectbox
st.title("Streamlit Top Navigation Bar Example")

# Create a selectbox at the top for navigation
page = st.selectbox("Choose a page:", ["Home", "About", "Contact"])

# Display content based on the selection
if page == "Home":
    st.header("Welcome to the Home Page")
    st.write("This is the home page content.")
elif page == "About":
    st.header("About Us")
    st.write("This is the about page content.")
elif page == "Contact":
    st.header("Contact Us")
    st.write("This is the contact page content.")
