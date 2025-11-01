import streamlit as st
from schemas.app_state_schemas.app_state import Views
from state_provider.state_provider_class import state_provider

def explore_expander():
    state = state_provider.get_state()
    
    def go_to_vitals():
        state.selected_view = Views.VITALS
        state_provider.save_state(state)

    def go_to_lab():
        state.selected_view = Views.LAB
        state_provider.save_state(state)

    with st.expander(label="Explore Data"):
        st.button("Vitals", key="vitals_button", on_click=go_to_vitals, width="stretch")
        st.button("Lab", key="lab_button", on_click=go_to_lab, width="stretch")
        
def forms_expander():
    state = state_provider.get_state()

    def go_to_lab_form():
        state.selected_view = Views.LAB_FORM
        state_provider.save_state(state)    

def render_sidebar():
    sidebar = st.sidebar
    state = state_provider.get_state()
    
    def go_to_homepage():
        state.selected_view = Views.HOMEPAGE
        state_provider.save_state(state)
    
    with sidebar:
        st.header("Navigation")
        from datetime import date, datetime

        # Ensure state.selected_time_range is a tuple of two datetimes, convert to dates for date_input
        default_range = (date.today(), date.today())
        if (isinstance(state.selected_time_range, tuple) and len(state.selected_time_range) == 2
            and all(isinstance(d, datetime) for d in state.selected_time_range)):
            time_range_dates = (state.selected_time_range[0].date(), state.selected_time_range[1].date())
        else:
            time_range_dates = default_range

        date_input_value = st.date_input("Select a date range", value=time_range_dates, help="Select the date range for exploration, visualization and export via RedCap CSV-File.")
        # Convert date to datetime if necessary
        def to_datetime(d):
            return datetime.combine(d, datetime.min.time()) if isinstance(d, date) else d
        if len(date_input_value) == 2:
            state.selected_time_range = (to_datetime(date_input_value[0]), to_datetime(date_input_value[1]))
            state_provider.save_state(state)
        if state.parsed_data:
            st.button("Overview", on_click=go_to_homepage, width="stretch")
            explore_expander()
            forms_expander()