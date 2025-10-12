import streamlit as st
from state_provider.state_provider import get_state


def render_homepage():
    st.header("Overview")
    state = get_state()
    if not state:
        st.info("""No state available to display. 
                Please upload a file.""")
        return
    st.subheader("Time Range")
    start = state.time_range[0].strftime("%d.%m.%Y")
    end = state.time_range[1].strftime("%d.%m.%Y")
    selected_start = state.selected_time_range[0].strftime("%d.%m.%Y")
    selected_end = state.selected_time_range[1].strftime("%d.%m.%Y")
    st.write(f"Available Time Range of Patient Record: {start} - {end}")
    st.markdown(f""" Containing in Total:
- **{len(state.parsed_data.vitals)}** Vitals  
- **{len(state.parsed_data.lab)}** Lab Results  
- **{len(state.parsed_data.ecmo) + len(state.parsed_data.impella)}** MCS Recordings  
- **{len(state.parsed_data.respiratory)}** Respiratory Values  
- **{len(state.parsed_data.medication)}** Medication entries
    """)
    st.write(f"Selected Time Range: {selected_start} - {selected_end}")

    st.subheader("MCS Time Range")
    st.markdown("##### ECMO")
    st.write(f"ECMO Time Range: ???")
    st.markdown("##### Impella")
    st.write(f"Impella Time Range: ???")

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