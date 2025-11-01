import streamlit as st
from state_provider.state_provider_class import state_provider
from datetime import datetime
import pandas as pd

def render_ecmo_time_ranges():
    ecmo_time_ranges = state_provider.get_device_time_ranges("ecmo")

    # Cleanup required to remove invalid entries, e.g. "ECMO-Durchtrittsstelle"
    clean_ecmo_time_ranges = []
    for device, start, end in ecmo_time_ranges:
        if "ecmo " in device.lower() and device.lower().startswith("ecmo"):
            clean_ecmo_time_ranges.append((device, start, end))

    if not len(clean_ecmo_time_ranges):
        st.write("No valid ECMO time ranges found.")
        return

    for device, start, end in clean_ecmo_time_ranges:
        st.markdown(f"**<u>{device}</u>: {start.strftime('%d.%m.%Y %H:%M')} - {end.strftime('%d.%m.%Y %H:%M')}**", unsafe_allow_html=True)

def render_impella_time_ranges():
    impella_time_ranges = state_provider.get_device_time_ranges("impella")

    # Cleanup
    clean_impella_time_ranges = []
    for device, start, end in impella_time_ranges:
        if "impella " in device.lower() and device.lower().startswith("impella"):
            clean_impella_time_ranges.append((device, start, end))

    if not len(clean_impella_time_ranges):
        st.write("No valid Impella time ranges found.")
        return

    for device, start, end in clean_impella_time_ranges:
        st.markdown(f"**<u>{device}</u>: {start.strftime('%d.%m.%Y %H:%M')} - {end.strftime('%d.%m.%Y %H:%M')}**", unsafe_allow_html=True)

def render_crrt_time_ranges():
    crrt_time_ranges = state_provider.get_device_time_ranges("crrt")

    if not len(crrt_time_ranges):
        st.write("No valid CRRT time ranges found.")
        return

    for device, start, end in crrt_time_ranges:
        st.markdown(f"**<u>{device}</u>: {start.strftime('%d.%m.%Y %H:%M')} - {end.strftime('%d.%m.%Y %H:%M')}**", unsafe_allow_html=True)

def render_set_selected_time_range_to_mcs_button():
    mcs_time_ranges = []
    mcs_time_ranges.extend(data for data in state_provider.get_device_time_ranges("impella"))
    mcs_time_ranges.extend(data for data in state_provider.get_device_time_ranges("ecmo"))
    print(mcs_time_ranges)

    if not len(mcs_time_ranges):
        return

    try:
        mcs_start_date = min(range.start for range in mcs_time_ranges)
        mcs_end_date = max(range.end for range in mcs_time_ranges)
    except ValueError:
        print("Error occurred while determining MCS time range.")
        return

    def set_mcs_range():
        state_provider.set_selected_time_range(mcs_start_date, mcs_end_date)

    st.button("Set Selected Time Range to MCS", on_click=set_mcs_range, help="Set the selected time range to the cumulative time span of MCS devices.")

def render_homepage():
    st.header("Overview")
    state = state_provider.get_state()
    
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
    render_set_selected_time_range_to_mcs_button()
    st.subheader("CRRT Time Range")
    render_crrt_time_ranges()