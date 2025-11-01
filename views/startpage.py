import streamlit as st
from state_provider.state_provider_class import state_provider
from schemas.app_state_schemas.app_state import Views


def render_startpage():
    state = state_provider.get_state()
    st.title("mLife Data Parser")
    st.write("Upload your CSV file 'Gesamte Akte' for processing:")
    st.markdown("\nWenn Sie eine Datei hochladen, wird diese Ansicht durch die Homepage ersetzt.")
    delimiter = st.selectbox(
            "Select delimiter:",
            options=[";", "|"],
            index=0,
            help="Choose ';' or '|' as the delimiter for the CSV file"
        )

    uploaded_file = st.file_uploader("Choose a file", type="csv")

    if uploaded_file is not None:
        # Parse and switch to homepage
        file = uploaded_file.read().decode("utf-8")
        state_provider.parse_data_to_state(file, delimiter)
        if state_provider.get_state() is not None:
            state_provider.update_state(selected_view=Views.HOMEPAGE)
        st.rerun()  # Refresh to show homepage