import streamlit as st
import numpy as np

st.set_page_config(
    page_title="Homepage",
    page_icon="🌟",
    layout="wide"
)

radio_opt=["Leakage Rate Trend %","File Review Score Trend %"]

selected_opt=st.radio(label="Choose the view",options=radio_opt)


