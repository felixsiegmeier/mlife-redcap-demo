from state_provider.state_provider import get_state, save_state, parse_data_to_state
from views.startpage import show_startpage
from views.homepage import show_homepage
from schemas.app_state_schemas.app_state import Views
from datetime import datetime

def run_app():
    state = get_state()

    if state.selected_view == Views.STARTPAGE:
        show_startpage()

    elif state.selected_view == Views.HOMEPAGE:
        show_homepage()

if __name__ == "__main__":
    run_app()
    