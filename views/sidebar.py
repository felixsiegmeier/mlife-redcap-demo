import streamlit as st
from schemas.app_state_schemas.app_state import Views
from state_provider.state_provider import get_state, save_state

def explore_expander():
    state = get_state()
    
    def go_to_vitals():
        state.selected_view = Views.VITALS
        save_state(state)

    def go_to_lab():
        state.selected_view = Views.LAB
        save_state(state)

    with st.expander(label="Explore Data"):
        st.button("Vitals", key="vitals_button", on_click=go_to_vitals, width="stretch")
        st.button("Lab", key="lab_button", on_click=go_to_lab, width="stretch")
        
def forms_expander():
    state = get_state()

    def go_to_lab_form():
        state.selected_view = Views.LAB_FORM
        save_state(state)

    with st.expander(label="RedCap Forms"):
        st.button("Lab", key="lab_form_button", on_click=go_to_lab_form, width="stretch")    

def render_sidebar():
    sidebar = st.sidebar
    state = get_state()
    
    def go_to_homepage():
        state.selected_view = Views.HOMEPAGE
        save_state(state)
    
    with sidebar:
        st.header("Navigation")
        from datetime import date, datetime

        # Ensure state.time_range is a tuple of two dates
        default_range = (date.today(), date.today())
        time_range = state.time_range if (
            isinstance(state.time_range, tuple) and len(state.time_range) == 2
            and all(isinstance(d, date) for d in state.time_range)
        ) else default_range

        date_input_value = st.date_input("Select a date range", value=time_range)
        # Convert date to datetime if necessary
        def to_datetime(d):
            return datetime.combine(d, datetime.min.time()) if isinstance(d, date) else d
        if len(date_input_value) == 2:
            state.selected_time_range = (to_datetime(date_input_value[0]), to_datetime(date_input_value[1]))
            save_state(state)
        if state.parsed_data:
            st.button("Overview", on_click=go_to_homepage, width="stretch")
            explore_expander()
            forms_expander()