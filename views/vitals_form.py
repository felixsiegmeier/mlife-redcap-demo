import streamlit as st
from typing import Any, Callable
import pandas as pd
from state_provider.state_provider import get_state, save_state
from services.value_aggregation.vitals_aggregator import create_vitals_entry
from schemas.db_schemas.vitals import (
    NirsLocation,
    VentilationType,
    VentilationSpecifics,
    VentilationMode,
    MobilizationLevel,
    AnticoagulationAgent,
    AntiPlateletAgent,
    Antibiotic,
    NutritionType,
    OtherOrganSupport,
    Medication,
    NarcoticsSedative,
    RenalReplacementTherapy,
    AcuteKidneyInjury,
    FluidBalancing,
)


VITALS_FIELDS = {
    "general": {
        "date": {"type": "date", "label": "Date of Measurement"},
        "mcs_last_24h": {"type": "checkbox", "label": "MCS last 24h"},
        "ecls_and_impella_last_24h": {"type": "checkbox", "label": "ECLS and Impella last 24h"},
        "day_of_mcs": {"type": "number", "label": "Day of MCS", "step": None},
    },
    "nirs": {
        "nirs.location": {"type": "multiselect", "label": "NIRS Location", "options": [e.value for e in NirsLocation]},
        "nirs.nirs_values.cerebral_left": {"type": "number", "label": "Cerebral Left NIRS Value", "step": None},
        "nirs.nirs_values.cerebral_right": {"type": "number", "label": "Cerebral Right NIRS Value", "step": None},
        "nirs.nirs_values.femoral_left": {"type": "number", "label": "Femoral Left NIRS Value", "step": None},
        "nirs.nirs_values.femoral_right": {"type": "number", "label": "Femoral Right NIRS Value", "step": None},
        "nirs.change_last_24h": {"type": "checkbox", "label": "Change in last 24 hours"},
        "nirs.change": {"type": "number", "label": "Change in NIRS Value", "step": None},
    },
    "hemodynamics": {
        "hemodynamics.heart_rate": {"type": "number", "label": "Heart Rate", "step": None},
        "hemodynamics.systolic_blood_pressure": {"type": "number", "label": "Systolic Blood Pressure", "step": None},
        "hemodynamics.diastolic_blood_pressure": {"type": "number", "label": "Diastolic Blood Pressure", "step": None},
        "hemodynamics.mean_arterial_pressure": {"type": "number", "label": "Mean Arterial Pressure", "step": None},
        "hemodynamics.central_venous_pressure": {"type": "number", "label": "Central Venous Pressure", "step": None},
        "hemodynamics.spO2": {"type": "number", "label": "SpO2", "step": None},
        "hemodynamics.pac.pcwp": {"type": "number", "label": "PCWP", "step": None},
        "hemodynamics.pac.spap": {"type": "number", "label": "SPAP", "step": None},
        "hemodynamics.pac.dpap": {"type": "number", "label": "DPAP", "step": None},
        "hemodynamics.pac.mpap": {"type": "number", "label": "MPAP", "step": None},
        "hemodynamics.pac.ci": {"type": "number", "label": "CI", "step": None},
    },
    "vasoactive_agents": {
        "vasoactive_agents.norepinephrine": {"type": "checkbox", "label": "Norepinephrine"},
        "vasoactive_agents.epinephrine": {"type": "checkbox", "label": "Epinephrine"},
        "vasoactive_agents.dopamine": {"type": "checkbox", "label": "Dopamine"},
        "vasoactive_agents.dobutamine": {"type": "checkbox", "label": "Dobutamine"},
        "vasoactive_agents.vasopressin": {"type": "checkbox", "label": "Vasopressin"},
        "vasoactive_agents.enoximone": {"type": "checkbox", "label": "Enoximone"},
        "vasoactive_agents.esmolol": {"type": "checkbox", "label": "Esmolol"},
        "vasoactive_agents.levosimendan": {"type": "checkbox", "label": "Levosimendan"},
        "vasoactive_agents.metaraminol": {"type": "checkbox", "label": "Metaraminol"},
        "vasoactive_agents.metoprolol": {"type": "checkbox", "label": "Metoprolol"},
        "vasoactive_agents.milrinone": {"type": "checkbox", "label": "Milrinone"},
        "vasoactive_agents.nicardipine": {"type": "checkbox", "label": "Nicardipine"},
        "vasoactive_agents.nitroglycerin": {"type": "checkbox", "label": "Nitroglycerin"},
        "vasoactive_agents.nitroprusside": {"type": "checkbox", "label": "Nitroprusside"},
        "vasoactive_agents.phenylephrine": {"type": "checkbox", "label": "Phenylephrine"},
        "vasoactive_agents.tolazoline": {"type": "checkbox", "label": "Tolazoline"},
        "vasoactive_agents.empressin": {"type": "checkbox", "label": "Empressin"},
        "vasoactive_agents.dobutamine_dose": {"type": "number", "label": "Dobutamine Dose", "step": None},
        "vasoactive_agents.epinephrine_dose": {"type": "number", "label": "Epinephrine Dose", "step": None},
        "vasoactive_agents.norepinephrine_dose": {"type": "number", "label": "Norepinephrine Dose", "step": None},
        "vasoactive_agents.milrinone_dose": {"type": "number", "label": "Milrinone Dose", "step": None},
        "vasoactive_agents.vasopressin_dose": {"type": "number", "label": "Vasopressin Dose", "step": None},
        "vasoactive_agents.empressin_dose": {"type": "number", "label": "Empressin Dose", "step": None},
    },
    "ventilation": {
        "ventilation.ventilation_type": {"type": "selectbox", "label": "Ventilation Type", "options": [e.value for e in VentilationType]},
        "ventilation.o2": {"type": "number", "label": "O2 Flow Rate (L/min)", "step": None},
        "ventilation.fio2": {"type": "number", "label": "FiO2 (%)", "step": None},
        "ventilation.ventilation_specifics": {"type": "selectbox", "label": "Ventilation Specifics", "options": [e.value for e in VentilationSpecifics]},
        "ventilation.ventilation_mode": {"type": "selectbox", "label": "Ventilation Mode", "options": [e.value for e in VentilationMode]},
        "ventilation.hfo_ventilation_rate": {"type": "number", "label": "HFO Ventilation Rate", "step": None},
        "ventilation.conventional_ventilation_rate": {"type": "number", "label": "Conventional Ventilation Rate", "step": None},
        "ventilation.mean_airway_pressure": {"type": "number", "label": "Mean Airway Pressure (mbar)", "step": None},
        "ventilation.peak_inspiratory_pressure": {"type": "number", "label": "Peak Inspiratory Pressure (mbar)", "step": None},
        "ventilation.positive_end_expiratory_pressure": {"type": "number", "label": "Positive End-Expiratory Pressure (mbar)", "step": None},
        "ventilation.prone_position": {"type": "checkbox", "label": "Prone Position"},
    },
    "neurology": {
        "neurology.rass_score": {"type": "number", "label": "RASS Score", "step": None},
        "neurology.glasgow_coma_scale": {"type": "number", "label": "Glasgow Coma Scale", "step": None},
        "neurology.mobilization_level": {"type": "selectbox", "label": "Mobilization Level", "options": [e.value for e in MobilizationLevel]},
    },
    "anticoagulation": {
        "anticoagulation.iv_anticoagulation": {"type": "checkbox", "label": "IV Anticoagulation"},
        "anticoagulation.iv_anticoagulation_agent": {"type": "selectbox", "label": "IV Anticoagulation Agent", "options": [e.value for e in AnticoagulationAgent]},
        "anticoagulation.anti_platelet_therapy": {"type": "checkbox", "label": "Anti-platelet Therapy"},
        "anticoagulation.anti_platelet_agents": {"type": "multiselect", "label": "Anti-platelet Agents", "options": [e.value for e in AntiPlateletAgent]},
    },
    "antimicrobial_treatment": {
        "antimicrobial_treatment.antibiotic_antimycotic_treatment": {"type": "checkbox", "label": "Antibiotic/Antimycotic Treatment"},
        "antimicrobial_treatment.specific_antibiotic_treatment": {"type": "multiselect", "label": "Specific Antibiotic Treatment", "options": [e.value for e in Antibiotic]},
        "antimicrobial_treatment.antiviral_treatment": {"type": "checkbox", "label": "Antiviral Treatment"},
        "antimicrobial_treatment.specific_antiviral_treatment": {"type": "text", "label": "Specific Antiviral Treatment"},
    },
    "nutrition": {
        "nutrition.nutrition_administered": {"type": "checkbox", "label": "Nutrition Administered"},
        "nutrition.specific_nutrition": {"type": "multiselect", "label": "Specific Nutrition", "options": [e.value for e in NutritionType]},
    },
    "transfusion": {
        "transfusion.transfusion_required": {"type": "checkbox", "label": "Transfusion Required"},
        "transfusion.thrombocyte_transfusion": {"type": "number", "label": "Thrombocyte Transfusion (units/24h)", "step": None},
        "transfusion.red_blood_cell_transfusion": {"type": "number", "label": "Red Blood Cell Transfusion (units/24h)", "step": None},
        "transfusion.fresh_frozen_plasma_transfusion": {"type": "number", "label": "Fresh Frozen Plasma Transfusion (units/24h)", "step": None},
        "transfusion.ppsb_administration": {"type": "number", "label": "PPSB Administration (IU/24h)", "step": None},
        "transfusion.fibrinogen_administration": {"type": "number", "label": "Fibrinogen Administration (g/24h)", "step": None},
        "transfusion.antithrombin_iii_administration": {"type": "number", "label": "Antithrombin III Administration (IU/24h)", "step": None},
        "transfusion.factor_xiii_administration": {"type": "number", "label": "Factor XIII Administration (IU/24h)", "step": None},
    },
    "organ_support": {
        "organ_support.other_organ_support": {"type": "multiselect", "label": "Other Organ Support", "options": [e.value for e in OtherOrganSupport]},
        "organ_support.medication": {"type": "multiselect", "label": "Medication", "options": [e.value for e in Medication]},
        "organ_support.narcotics_sedative_agents": {"type": "multiselect", "label": "Narcotics/Sedative Agents", "options": [e.value for e in NarcoticsSedative]},
    },
    "kidney_function": {
        "kidney_function.renal_replacement_therapy": {"type": "selectbox", "label": "Renal Replacement Therapy", "options": [e.value for e in RenalReplacementTherapy]},
        "kidney_function.total_urine_output": {"type": "number", "label": "Total Urine Output", "step": None},
        "kidney_function.acute_kidney_injury": {"type": "selectbox", "label": "Acute Kidney Injury", "options": [e.value for e in AcuteKidneyInjury]},
        "kidney_function.total_output_renal_replacement": {"type": "number", "label": "Total Output via Renal Replacement Therapy (ml)", "step": None},
        "kidney_function.fluid_balancing_type": {"type": "selectbox", "label": "Fluid Balancing Type", "options": [e.value for e in FluidBalancing]},
        "kidney_function.fluid_balancing": {"type": "number", "label": "Fluid Balancing", "step": None},
    },
}

class VitalsFormUI:
    """Handles the UI for vitals form creation and editing."""
    
    def __init__(self, state: Any) -> None:
        """Initialize with the application state."""
    self.state = state
    self.value_strategy = "median"
    
    def show_update_hint(self) -> None:
        """Set a flag to show update hint when value strategy changes."""
        st.session_state['show_update_hint'] = True
    
    def render_controls(self) -> None:
        """Render the controls for selecting vitals value calculation and creating/updating forms."""
        self.value_strategy = st.selectbox("Value Calculation Method", options=["median", "mean", "last", "first"], index=0, key="value_strategy_method", on_change=self.show_update_hint)
        if st.session_state.get('show_update_hint', False):
            st.info("Please press the 'Create/Update Vitals Form for selected Time Range' button to apply the changes.")
        if st.button("Create/Update Vitals Form for selected Time Range"):
            create_vitals_form_with_value_strategy(self.value_strategy)
            st.session_state['show_update_hint'] = False
            st.rerun()

    def update_vitals_field(self, index: int, field: str) -> Callable[[], None]:
        """Create a callback function to update a vitals field for a specific entry."""
        def inner() -> None:
            value = st.session_state[f'{index}_{field}']
            if field in ['nirs.location', 'anticoagulation.anti_platelet_agents', 'antimicrobial_treatment.specific_antibiotic_treatment', 'nutrition.specific_nutrition', 'organ_support.other_organ_support', 'organ_support.medication', 'organ_support.narcotics_sedative_agents']:
                # Handle multiselect
                if field == 'nirs.location':
                    value = [NirsLocation(v) for v in value]
                elif field == 'anticoagulation.anti_platelet_agents':
                    value = [AntiPlateletAgent(v) for v in value]
                elif field == 'antimicrobial_treatment.specific_antibiotic_treatment':
                    value = [Antibiotic(v) for v in value]
                elif field == 'nutrition.specific_nutrition':
                    value = [NutritionType(v) for v in value]
                elif field == 'organ_support.other_organ_support':
                    value = [OtherOrganSupport(v) for v in value]
                elif field == 'organ_support.medication':
                    value = [Medication(v) for v in value]
                elif field == 'organ_support.narcotics_sedative_agents':
                    value = [NarcoticsSedative(v) for v in value]
            elif field in ['ventilation.ventilation_type', 'ventilation.ventilation_specifics', 'ventilation.ventilation_mode', 'neurology.mobilization_level', 'anticoagulation.iv_anticoagulation_agent', 'kidney_function.renal_replacement_therapy', 'kidney_function.acute_kidney_injury', 'kidney_function.fluid_balancing_type']:
                # Handle selectbox enums
                if field == 'ventilation.ventilation_type':
                    value = VentilationType(value)
                elif field == 'ventilation.ventilation_specifics':
                    value = VentilationSpecifics(value)
                elif field == 'ventilation.ventilation_mode':
                    value = VentilationMode(value)
                elif field == 'neurology.mobilization_level':
                    value = MobilizationLevel(value)
                elif field == 'anticoagulation.iv_anticoagulation_agent':
                    value = AnticoagulationAgent(value)
                elif field == 'kidney_function.renal_replacement_therapy':
                    value = RenalReplacementTherapy(value)
                elif field == 'kidney_function.acute_kidney_injury':
                    value = AcuteKidneyInjury(value)
                elif field == 'kidney_function.fluid_balancing_type':
                    value = FluidBalancing(value)
            state = get_state()
            if '.' in field:
                parts = field.split('.')
                obj = state.vitals_form[index]
                for part in parts[:-1]:
                    if not hasattr(obj, part) or getattr(obj, part) is None:
                        # Initialize nested object if None
                        # This is simplified; in practice, you might need to create instances
                        pass
                    obj = getattr(obj, part)
                setattr(obj, parts[-1], value)
            else:
                setattr(state.vitals_form[index], field, value)
            save_state(state)
        return inner
    
    def get_nested_value(self, obj: Any, field: str) -> Any:
        """Get a nested attribute value from an object."""
        if '.' in field:
            parts = field.split('.')
            for part in parts[:-1]:
                obj = getattr(obj, part)
                if obj is None:
                    return None
            return getattr(obj, parts[-1])
        else:
            return getattr(obj, field)
    
    def render_widget(self, config: dict, value: Any, index: int, field: str) -> None:
        """Render a Streamlit widget based on the config."""
        key = f'{index}_{field}'
        if config["type"] == "number":
            st.session_state[key] = value
            st.number_input(config["label"], value=value, step=config.get("step"), key=key, on_change=self.update_vitals_field(index, field))
        elif config["type"] == "checkbox":
            st.session_state[key] = value
            st.checkbox(config["label"], value=value, key=key, on_change=self.update_vitals_field(index, field))
        elif config["type"] == "selectbox":
            options = config["options"]
            current_value = value.value if hasattr(value, 'value') else value
            st.session_state[key] = current_value
            sel_index = options.index(current_value) if current_value in options else 0
            st.selectbox(config["label"], options=options, index=sel_index, key=key, on_change=self.update_vitals_field(index, field))
        elif config["type"] == "multiselect":
            options = config["options"]
            current_value = [v.value if hasattr(v, 'value') else v for v in value] if value else []
            st.session_state[key] = current_value
            st.multiselect(config["label"], options=options, default=current_value, key=key, on_change=self.update_vitals_field(index, field))
        elif config["type"] == "date":
            st.session_state[key] = value
            st.date_input(config["label"], value=value, key=key, on_change=self.update_vitals_field(index, field))
        elif config["type"] == "text":
            st.session_state[key] = value
            st.text_input(config["label"], value=value, key=key, on_change=self.update_vitals_field(index, field))
    
    def display_vitals_entry(self, index: int) -> None:
        """Display the editable form for a single vitals entry."""
        vitals_entry = self.state.vitals_form[index]
        st.header("Edit Vitals Entry")
        
        for group, fields in VITALS_FIELDS.items():
            with st.expander(group.replace('_', ' ').title()):
                for field, config in fields.items():
                    value = self.get_nested_value(vitals_entry, field)
                    self.render_widget(config, value, index, field)
    
    def render_entries(self) -> None:
        """Render all vitals entries as expanders."""
        if self.state.vitals_form:
            for i in range(len(self.state.vitals_form)):
                with st.expander(f"Vitals Entry for {self.state.vitals_form[i].date.date()}", width="stretch"):
                    self.display_vitals_entry(i)

    def render_submit_button(self) -> None:
        """Render the submit button for the vitals form."""
        if self.state.vitals_form:
            if st.button("Send Vitals Data to RedCap"):
                st.warning("Not implemented")

    def vitals_form(self) -> None:
        """Main method to render the entire vitals form UI."""
        st.title("Vitals Form")
        self.render_controls()
        self.render_entries()
        self.render_submit_button()

def create_vitals_form_with_value_strategy(value_strategy):
    state = get_state()
    state.vitals_form = []
    if state.selected_time_range:
        start_date, end_date = state.selected_time_range
        current_date = start_date
        while current_date <= end_date:
            date = current_date.date()
            vitals_entry = create_vitals_entry(date, value_strategy)
            state.vitals_form.append(vitals_entry)
            current_date += pd.Timedelta(days=1)
    save_state(state)

def vitals_form() -> None:
    """Entry point for the vitals form view."""
    state = get_state()
    ui = VitalsFormUI(state)
    ui.vitals_form()

