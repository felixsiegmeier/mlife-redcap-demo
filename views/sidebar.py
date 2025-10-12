import streamlit as st
from schemas.app_state_schemas.app_state import Views
from state_provider.state_provider import get_state, save_state


def render_sidebar():
    sidebar = st.sidebar
    state = get_state()
    time_range = state.get("time_range", (None, None))
    
    with sidebar:
        st.header("Navigation")
        start, stop = st.date_input("Select a date range", value=time_range)
        st.button("Go to Startpage", on_click=lambda: st.session_state.selected_view = Views.STARTPAGE)
        st.button("Go to Homepage", on_click=lambda: st.session_state.selected_view = Views.HOMEPAGE)