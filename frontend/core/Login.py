import streamlit as st
import yaml
import os
from streamlit_extras.stateful_button import button

# Load YAML credentials
def load_credentials(file_path="C:/Users/abhishek221057/OneDrive - EXLService.com (I) Pvt. Ltd/Desktop/AADJ_Dashboards/dashboards_/credentials.yaml"):
    with open(file_path, "r") as file:
        return yaml.safe_load(file)

# Authenticate user
def authenticate_user(username, password, credentials):
    user_data = credentials.get("credentials", {}).get("usernames", {}).get(username)
    if user_data and user_data.get("password") == password:
        return user_data
    return None

# Main function
def main():
    st.set_page_config(page_title="Login", layout="centered")
    credentials = load_credentials()

    # Session state for login
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # If not logged in
    if not st.session_state.logged_in:
        st.title("Login Page")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")

        if submitted:
            user_data = authenticate_user(username, password, credentials)
            if user_data:
                st.session_state.logged_in = True
                st.session_state.user_data = user_data
                query_params = st.query_params
                query_params['page'] = ["Home"]
                # query_params.get("page") == ["Home"]
                # st.success(f"Welcome, {user_data['first_name']}!")
                st.rerun()
            else:
                st.error("Invalid username or password.")
    else:
        # Redirect to Page 1
        query_params = st.query_params
        if query_params.get("page") == ["Home"]:
            st.write("Redirecting to Page 1...")
            st.rerun()

if __name__ == "__main__":
    main()
