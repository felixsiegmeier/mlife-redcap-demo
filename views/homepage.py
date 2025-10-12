import streamlit as st
from state_provider.state_provider import get_state
from datetime import datetime
import pandas as pd

def render_ecmo_time_ranges():
    state = get_state()
    try:
        df = state.parsed_data.ecmo
        ecmos = df['category'].dropna().unique().tolist()
        for ecmo in ecmos:
            try:
                ts = df[df['category'] == ecmo]['timestamp']
                ts = pd.to_datetime(ts, errors='coerce').dropna()
                if ts.empty:
                    raise ValueError("Keine gültigen Timestamps gefunden")
                start = ts.min().date().strftime("%d.%m.%Y")
                end = ts.max().date().strftime("%d.%m.%Y")
                st.markdown(f"**<u>{ecmo}</u>: {start} - {end}**", unsafe_allow_html=True)
            except Exception:
                pass
    except Exception:
        st.write("No valid ECMO data available")
        return
    
def render_impella_time_ranges():
    state = get_state()
    try:
        df = state.parsed_data.impella
        impellas = df['category'].dropna().unique().tolist()
        for impella in impellas:
            try:
                ts = df[df['category'] == impella]['timestamp']
                ts = pd.to_datetime(ts, errors='coerce').dropna()
                if ts.empty:
                    raise ValueError("Keine gültigen Timestamps gefunden")
                start = ts.min().date().strftime("%d.%m.%Y")
                end = ts.max().date().strftime("%d.%m.%Y")
                st.markdown(f"**<u>{impella}</u>: {start} - {end}**", unsafe_allow_html=True)
            except Exception:
                pass
    except Exception:
        st.write("No valid Impella data available")
        return

def render_crrt_time_ranges():
    state = get_state()
    try:
        df = state.parsed_data.crrt
        crrts = df['category'].dropna().unique().tolist()
        for crrt in crrts:
            try:
                ts = df[df['category'] == crrt]['timestamp']
                ts = pd.to_datetime(ts, errors='coerce').dropna()
                if ts.empty:
                    raise ValueError("Keine gültigen Timestamps gefunden")
                start = ts.min().date().strftime("%d.%m.%Y")
                end = ts.max().date().strftime("%d.%m.%Y")
                st.markdown(f"**<u>{crrt}</u>: {start} - {end}**", unsafe_allow_html=True)
            except Exception:
                pass
    except Exception:
        st.write("No valid CRRT data available")
        return


def render_homepage():
    st.header("Overview")
    state = get_state()
    
    parsed = getattr(state, "parsed_data", None)
    if not parsed:
        st.info("No parsed data available.")
        return
    
    if not state:
        st.info("""No state available to display. 
                Please upload a file.""")
        return
    st.subheader("Time Range")
    start = state.time_range[0].strftime("%d.%m.%Y")
    end = state.time_range[1].strftime("%d.%m.%Y")
    selected_start = state.selected_time_range[0].strftime("%d.%m.%Y")
    selected_end = state.selected_time_range[1].strftime("%d.%m.%Y")
    st.write(f"Available Time Range of Patient Record: **{start} - {end}**")
    st.markdown(f""" Containing in Total:
- **{len(state.parsed_data.vitals)}** Vitals  
- **{len(state.parsed_data.lab)}** Lab Results  
- **{len(state.parsed_data.ecmo) + len(state.parsed_data.impella)}** MCS Recordings  
- **{len(state.parsed_data.respiratory)}** Respiratory Values  
- **{len(state.parsed_data.medication)}** Medication entries
    """)
    st.write(f"Selected Time Range: **{selected_start} - {selected_end}**")

    st.subheader("MCS Time Range")
    render_ecmo_time_ranges()
    render_impella_time_ranges()

    st.subheader("CRRT Time Range")
    render_crrt_time_ranges()