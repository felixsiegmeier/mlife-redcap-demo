from state_provider.state_provider import get_state, save_state, parse_data_to_state
from views.sidebar import render_sidebar
from views.startpage import render_startpage
from views.homepage import render_homepage
from views.vitals_data import render_vitals_data
from views.lab_data import render_lab_data
from schemas.app_state_schemas.app_state import Views
from datetime import datetime
import streamlit as st

def run_app():
    state = get_state()
   
    if not state.selected_view == Views.STARTPAGE:
        render_sidebar()

    if state.selected_view == Views.STARTPAGE:
        render_startpage()
        with st.sidebar:
            st.header("Please upload a file")

    elif state.selected_view == Views.HOMEPAGE:
        render_homepage()
        
    elif state.selected_view == Views.VITALS:
        render_vitals_data()

    elif state.selected_view == Views.LAB:
        render_lab_data()

if __name__ == "__main__":
    run_app()
    