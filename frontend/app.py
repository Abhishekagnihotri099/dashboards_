import streamlit as st
import requests

# Initialize session state
if "auth_token" not in st.session_state:
    st.session_state["auth_token"] = None

# API Endpoints
LOGIN_API_URL = "http://127.0.0.1:8000/api/login/"  # Replace with your Django backend URL

def login(username, password):
    """Authenticate user with the Django backend."""
    try:
        response = requests.post(LOGIN_API_URL, json={"username": username, "password": password})
        if response.status_code == 200:
            tokens = response.json()
            st.session_state["auth_token"] = tokens["access"]
            st.success("Login successful!")
        else:
            st.error("Invalid username or password.")
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to connect to backend: {e}")

def logout():
    """Clear the authentication token and logout."""
    st.session_state["auth_token"] = None
    st.experimental_rerun()

# Render Login Page
def render_login_page():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        login(username, password)

# Main App
def main():
    if st.session_state["auth_token"] is None:
        render_login_page()
    else:
        # Show navigation menu
        st.sidebar.title("Navigation")
        page = st.sidebar.radio("Go to", ["Dashboard1", "Dashboard2", "Logout"])

        if page == "Logout":
            logout()

        elif page == "Dashboard1":
            st.write("Dashboard 1 content.")
            # Include dashboard logic here

        elif page == "Dashboard2":
            st.write("Dashboard 2 content.")
            # Include dashboard logic here

if __name__ == "__main__":
    main()
