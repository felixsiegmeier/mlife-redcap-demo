from state_provider.state_provider_class import state_provider
from views.sidebar import render_sidebar
from views.startpage import render_startpage
from views.homepage import render_homepage
from views.vitals_data import render_vitals_data
from views.lab_data import render_lab_data
from views.lab_form import  lab_form
from schemas.app_state_schemas.app_state import Views
from datetime import datetime
import streamlit as st

def run_app():

    if not state_provider.get_selected_view() == Views.STARTPAGE:
        render_sidebar()

    if state_provider.get_selected_view() == Views.STARTPAGE:
        render_startpage()
        with st.sidebar:
            st.header("Please upload a file")

    elif state_provider.get_selected_view() == Views.HOMEPAGE:
        render_homepage()

    elif state_provider.get_selected_view() == Views.VITALS:
        render_vitals_data()

    elif state_provider.get_selected_view() == Views.LAB:
        render_lab_data()

    elif state_provider.get_selected_view() == Views.LAB_FORM:
        lab_form()

if __name__ == "__main__":
    run_app()
    