import streamlit as st
from state_provider.state_provider import get_state


def show_homepage():
    st.header("Homepage")
    state = get_state()
    if not state:
        st.info("No state available to display.")
        return

    parsed = getattr(state, "parsed_data", None)
    if not parsed:
        st.info("No parsed data available.")
        return

    vitals = getattr(parsed, "vitals", None)
    if vitals is None:
        st.info("No vitals available in parsed data.")
        return

    st.subheader("Vitals")
    st.write(vitals)