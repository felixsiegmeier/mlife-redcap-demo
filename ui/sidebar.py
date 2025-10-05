import streamlit as st
import pandas as pd
from typing import Optional, Tuple


def render_sidebar_navigation(dfs: list) -> Tuple[Optional[pd.Timestamp], Optional[pd.Timestamp], str]:
    """Render a compact sidebar containing only the global date range picker and a view selector.

    Returns (start_dt, end_dt, view_choice)
    """
    all_ts = []
    for df in dfs:
        if df is not None and 'timestamp_parsed' in df.columns and df['timestamp_parsed'].notna().any():
            all_ts.append(df['timestamp_parsed'].min())
            all_ts.append(df['timestamp_parsed'].max())

    if all_ts:
        global_min = min(all_ts)
        global_max = max(all_ts)
        date_range = st.sidebar.date_input("Globaler Zeitraum (inkl.)", value=(global_min.date(), global_max.date()), key="global_daterange")
        if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
            sd, ed = date_range
        else:
            sd = ed = date_range
        try:
            start_dt = pd.to_datetime(sd)
            end_dt = pd.to_datetime(ed) + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
            if isinstance(start_dt, (pd.DatetimeIndex,)):
                start_dt = start_dt[0]
            if isinstance(end_dt, (pd.DatetimeIndex,)):
                end_dt = end_dt[0]
        except Exception:
            st.sidebar.info("Fehler beim Parsen der globalen Datumsauswahl")
            start_dt, end_dt = None, None
    else:
        st.sidebar.info("Keine Zeitstempel in den Daten gefunden — globaler Zeitraum deaktiviert")
        start_dt, end_dt = None, None

    # View navigation: render as vertical buttons (persist selection in session_state)
    st.sidebar.markdown("### Ansicht")
    options = ["Vitals", "Respirator", "Labor", "MCS - ECMO", "MCS - Impella", "RRT", "Übersicht"]

    # initialize session_state value if not present
    if "view_choice" not in st.session_state:
        st.session_state["view_choice"] = options[0]

    def _set_view(choice: str):
        st.session_state["view_choice"] = choice

    # render each option as a button stacked vertically; mark the active one with a check
    for opt in options:
        key_safe = f"view_{opt.replace(' ', '_').replace('-', '_')}"
        label = f"✔️ {opt}" if st.session_state.get("view_choice") == opt else opt
        # center the button by placing it in the middle of three columns
        # give the middle column more space so the button is centered but not too narrow
        cols = st.sidebar.columns([1, 6, 1])
        with cols[1]:
            st.button(label, key=key_safe, on_click=_set_view, args=(opt,))

    # guarantee a string return value
    view_choice = st.session_state.get("view_choice") or options[0]

    return start_dt, end_dt, view_choice
