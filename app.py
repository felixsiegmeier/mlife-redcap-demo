from pathlib import Path
from typing import Optional
from state_provider.state_provider import get_state, save_state, parse_data_to_state
from views import show_startpage, show_homepage
from datetime import datetime
import streamlit as st

def run_app():
    # show_startpage returns (uploaded_file, delimiter)
    # okay das geht alles nicht... hier ändern, sodass 
    # direkt der view (startpage, homepage etc.) anhand des states selected_view
    # ausgewählt wird (diesen implementieren als nächstes!)
    uploaded_file, delimiter = show_startpage()

    if uploaded_file is not None:
        file = uploaded_file.read().decode("utf-8")
        state = parse_data_to_state(file, delimiter)
        show_homepage()
    

if __name__ == "__main__":
    run_app()
    