import streamlit as st
from schemas.app_state_schemas.app_state import Views
from state_provider.state_provider import get_state, save_state


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
        st.button("Overview", on_click=go_to_homepage)