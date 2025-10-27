
"""
Lab Form Module - Program Flow Summary

Program Flow:
1. lab_form() is the entry point, called from the main app.
2. It retrieves the application state using get_state().
3. Instantiates LabFormUI with the state.
4. Calls ui.lab_form(), which renders the entire UI:
   - Title
   - Controls (selectbox for value calculation method, update hint, create/update button)
   - Lab entries as expanders (editable forms for each day)
   - Submit button (placeholder for RedCap integration)
5. User interactions:
   - Changing the selectbox triggers show_update_hint(), setting a session_state flag to show an info message.
    - Pressing the create/update button calls create_lab_form_with_value_strategy(), which:
     - Clears existing lab_form in state
     - Iterates over selected_time_range, creating lab entries via create_lab_entry()
     - Saves state
   - Then sets the hint flag to False and reruns the app.
6. Each lab entry is editable via widgets (number_input, checkbox, selectbox, date_input) with on_change callbacks that update the state and save it.
7. create_lab_entry() aggregates lab data from parsed_data based on the selected method (median, mean, last, first) for each parameter.

Key Components:
- LabFormUI class: Encapsulates UI logic and state management.
- LAB_FIELDS dict: Defines field configurations for dynamic rendering.
- Callbacks ensure real-time updates and persistence via state_provider.
"""

import streamlit as st
from typing import Any, Callable
import pandas as pd
from state_provider.state_provider import get_state, save_state
from services.value_aggregation.lab_aggregator import create_lab_entry
from schemas.db_schemas.lab import WithdrawalSite


LAB_FIELDS = {
    "general": {
        "mcs_last_24h": {"type": "checkbox", "label": "MCS last 24h"},
        "ecls_and_impella_last_24h": {"type": "checkbox", "label": "ECLS and Impella last 24h"},
        "day_of_mcs": {"type": "number", "label": "Day of MCS", "step": None},
        "withdrawal_site": {"type": "selectbox", "label": "Withdrawal Site", "options": [e.value for e in WithdrawalSite]},
        "date_of_assessment": {"type": "date", "label": "Date of Assessment"},
        "time_of_assessment": {"type": "date", "label": "Time of Assessment"},
    },
    "arterial_blood_gas": {
        "arterial_blood_gas.pco2": {"type": "number", "label": "PCO2 (mmHg)", "step": None},
        "arterial_blood_gas.po2": {"type": "number", "label": "PO2 (mmHg)", "step": None},
        "arterial_blood_gas.ph": {"type": "number", "label": "pH", "step": None},
        "arterial_blood_gas.hco3": {"type": "number", "label": "HCO3 (mmol/L)", "step": None},
        "arterial_blood_gas.be": {"type": "number", "label": "BE (mmol/L)", "step": None},
        "arterial_blood_gas.sao2": {"type": "number", "label": "SaO2 (%)", "step": None},
        "arterial_blood_gas.kalium": {"type": "number", "label": "Kalium (mmol/L)", "step": None},
        "arterial_blood_gas.natrium": {"type": "number", "label": "Natrium (mmol/L)", "step": None},
        "arterial_blood_gas.glucose": {"type": "number", "label": "Glucose (mg/dL)", "step": None},
        "arterial_blood_gas.lactate": {"type": "number", "label": "Lactate (mg/dL)", "step": None},
        "arterial_blood_gas.svo2": {"type": "number", "label": "SvO2 (%)", "step": None},
    },
    "blood_count": {
        "wbc": {"type": "number", "label": "WBC (10^9/L)", "step": None},
        "hb": {"type": "number", "label": "HB (g/dL)", "step": None},
        "hct": {"type": "number", "label": "HCT (%)", "step": None},
        "plt": {"type": "number", "label": "PLT (10^9/L)", "step": None},
    },
    "coagulation": {
        "ptt": {"type": "number", "label": "PTT (s)", "step": None},
        "quick": {"type": "number", "label": "Quick (%)", "step": None},
        "inr": {"type": "number", "label": "INR", "step": None},
        "act": {"type": "number", "label": "ACT (s)", "step": None},
    },
    "enzymes": {
        "ck": {"type": "number", "label": "CK (U/L)", "step": None},
        "ck_mb": {"type": "number", "label": "CK-MB (U/L)", "step": None},
        "ggt": {"type": "number", "label": "GGT (U/L)", "step": None},
        "ldh": {"type": "number", "label": "LDH (U/L)", "step": None},
        "lipase": {"type": "number", "label": "Lipase (U/L)", "step": None},
    },
    "other": {
        "albumin": {"type": "number", "label": "Albumin", "step": None},
        "crp": {"type": "number", "label": "CRP", "step": None},
        "pct": {"type": "number", "label": "PCT (ng/mL)", "step": None},
        "free_hb": {"type": "number", "label": "Free HB (mg/dL)", "step": None},
        "haptoglobin": {"type": "number", "label": "Haptoglobin", "step": None},
        "total_bilirubin": {"type": "number", "label": "Total Bilirubin (mg/dL)", "step": None},
        "creatinine": {"type": "number", "label": "Creatinine (mg/dL)", "step": None},
        "urea": {"type": "number", "label": "Urea (mg/dL)", "step": None},
        "creatinine_clearance": {"type": "number", "label": "Creatinine Clearance (mL/min/1.73m²)", "step": None},
    },
}

class LabFormUI:
    """Handles the UI for lab form creation and editing."""
    
    def __init__(self, state: Any) -> None:
        """Initialize with the application state."""
        self.state = state
        self.value_strategy = "median"
    
    def show_update_hint(self) -> None:
        """Set a flag to show update hint when value strategy changes."""
        st.session_state['show_update_hint'] = True
    
    def render_controls(self) -> None:
        """Render the controls for selecting lab value calculation and creating/updating forms."""
        self.value_strategy = st.selectbox("Value Calculation Method", options=["median", "mean", "last", "first"], index=0, key="value_strategy_method", on_change=self.show_update_hint)
        if st.session_state.get('show_update_hint', False):
            st.info("Please press the 'Create/Update Lab Form for selected Time Range' button to apply the changes.")
        if st.button("Create/Update Lab Form for selected Time Range"):
            create_lab_form_with_value_strategy(self.value_strategy)
            st.session_state['show_update_hint'] = False
            st.rerun()

    def update_lab_field(self, index: int, field: str) -> Callable[[], None]:
        """Create a callback function to update a lab field for a specific entry."""
        def inner() -> None:
            value = st.session_state[f'{index}_{field}']
            if field == 'withdrawal_site':
                value = WithdrawalSite(value)
            state = get_state()
            if '.' in field:
                parts = field.split('.')
                obj = state.lab_form[index]
                for part in parts[:-1]:
                    obj = getattr(obj, part)
                setattr(obj, parts[-1], value)
            else:
                setattr(state.lab_form[index], field, value)
            save_state(state)
        return inner
    
    def get_nested_value(self, obj: Any, field: str) -> Any:
        """Get a nested attribute value from an object."""
        if '.' in field:
            parts = field.split('.')
            for part in parts[:-1]:
                obj = getattr(obj, part)
            return getattr(obj, parts[-1])
        else:
            return getattr(obj, field)
    
    def render_widget(self, config: dict, value: Any, index: int, field: str) -> None:
        """Render a Streamlit widget based on the config."""
        key = f'{index}_{field}'
        
        # Nur den Session State setzen wenn der Key noch nicht existiert
        if key not in st.session_state:
            if config["type"] == "selectbox":
                current_value = value.value if hasattr(value, 'value') else value
                st.session_state[key] = current_value
            else:
                st.session_state[key] = value
        
        if config["type"] == "number":
            st.number_input(config["label"], step=config.get("step"), key=key, on_change=self.update_lab_field(index, field))
        elif config["type"] == "checkbox":
            st.checkbox(config["label"], key=key, on_change=self.update_lab_field(index, field))
        elif config["type"] == "selectbox":
            options = config["options"]
            st.selectbox(config["label"], options=options, key=key, on_change=self.update_lab_field(index, field))
        elif config["type"] == "date":
            st.date_input(config["label"], key=key, on_change=self.update_lab_field(index, field))
    
    def display_lab_entry(self, index: int) -> None:
        """Display the editable form for a single lab entry."""
        lab_entry = self.state.lab_form[index]
        st.header("Edit Lab Entry")
        
        for group, fields in LAB_FIELDS.items():
            if group == "arterial_blood_gas":
                with st.expander("Arterial Blood Gas"):
                    for field, config in fields.items():
                        value = self.get_nested_value(lab_entry, field)
                        self.render_widget(config, value, index, field)
            else:
                st.subheader(group.replace('_', ' ').title())
                for field, config in fields.items():
                    value = self.get_nested_value(lab_entry, field)
                    self.render_widget(config, value, index, field)
    
    def render_entries(self) -> None:
        """Render all lab entries as expanders."""
        if self.state.lab_form:
            for i in range(len(self.state.lab_form)):
                with st.expander(f"Lab Entry for {self.state.lab_form[i].date.date()}", width="stretch"):
                    self.display_lab_entry(i)

    def render_submit_button(self) -> None:
        """Render the submit button for the lab form."""
        if self.state.lab_form:
            if st.button("Send Lab Data to RedCap"):
                st.warning("Not implemented")

    def lab_form(self) -> None:
        """Main method to render the entire lab form UI."""
        st.title("Lab Form")
        self.render_controls()
        self.render_entries()
        self.render_submit_button()

def create_lab_form_with_value_strategy(value_strategy):
    state = get_state()
    state.lab_form = []
    if state.selected_time_range:
        start_date, end_date = state.selected_time_range
        current_date = start_date
        while current_date <= end_date:
            date = current_date.date()
            lab_entry = create_lab_entry(date, value_strategy)
            print(lab_entry)
            state.lab_form.append(lab_entry)
            current_date += pd.Timedelta(days=1)
    save_state(state)

def lab_form() -> None:
    """Entry point for the lab form view."""
    state = get_state()
    ui = LabFormUI(state)
    ui.lab_form()