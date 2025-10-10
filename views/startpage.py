import streamlit as st


def show_startpage():
    """Render a simple start/introduction page.

    Note: the actual file uploader and delimiter selection are rendered in
    `app.py` so that the startpage can be hidden immediately when a file is
    present.
    """
    st.title("mLife Data Parser")
    st.write("Upload your CSV file 'Gesamte Akte' for processing:")
    st.markdown("\nWenn Sie eine Datei hochladen, wird diese Ansicht durch die Homepage ersetzt.")
