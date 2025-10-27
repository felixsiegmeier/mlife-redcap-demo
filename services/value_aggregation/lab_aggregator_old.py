from state_provider.state_provider import get_state
from state_provider.state_provider_class import StateProvider
import pandas as pd
from schemas.db_schemas.lab import LabModel, WithdrawalSite
from datetime import datetime

def get_lab_value(date, category=None, parameter=None, value_strategy="median"):
    state = get_state()
    if state.parsed_data and state.parsed_data.lab is not None:
        lab_data = state.parsed_data.lab
        if category and parameter:
            filtered_data = lab_data[
                (lab_data["timestamp"].dt.date == date) &
                (lab_data["category"] == category) &
                (lab_data["parameter"] == parameter)
            ]
            if not filtered_data.empty:
                try:
                    # Convert values to numeric, coercing errors to NaN
                    numeric_values = pd.to_numeric(filtered_data["value"], errors='coerce')
                    
                    if value_strategy == "median":
                        result = numeric_values.median()
                    elif value_strategy == "mean":
                        result = numeric_values.mean()
                    elif value_strategy == "last":
                        result = numeric_values.iloc[-1]
                    elif value_strategy == "first":
                        result = numeric_values.iloc[0]
                    else:
                        result = numeric_values.median()
                    
                    # Return None if result is NaN, otherwise return the float value
                    return None if pd.isna(result) else float(result)
                    
                except Exception:
                    # If anything goes wrong, return None
                    return None
    return None

def create_lab_entry(date, value_strategy="median"):
    arterial_blood_gas = ArterialBloodGasModel(
        pco2=get_lab_value(date, "Blutgase arteriell", "PCO2 [mmHg]"),
        po2=get_lab_value(date, "Blutgase arteriell", "PO2 [mmHg]"),
        ph=get_lab_value(date, "Blutgase arteriell", "PH"),
        hco3=get_lab_value(date, "Blutgase arteriell", "HCO3 [mmol·L⁻¹]"),
        be=get_lab_value(date, "Blutgase arteriell", "ABEc [mmol·L⁻¹]"),
        sao2=get_lab_value(date, "Blutgase arteriell", "O2-SAETTIGUNG [%]"),
        kalium=get_lab_value(date, "Blutgase arteriell", "KALIUM(BG) [mmol·L⁻¹]"),
        natrium=get_lab_value(date, "Blutgase arteriell", "NATRIUM(BG) [mmol·L⁻¹]"),
        glucose=get_lab_value(date, "Blutgase arteriell", "GLUCOSE(BG) [mg·dL⁻¹]"),
        lactate=get_lab_value(date, "Blutgase arteriell", "LACTAT(BG) [mg·dL⁻¹]"),
        svo2=get_lab_value(date, "Blutgase venös", "O2-SAETTIGUNG [%]")
    )
    state = get_state()
    ecmo_last_24h = False
    impella_last_24h = False

    if state.parsed_data:
        # Check for ECMO entries on the given date or the day before
        if hasattr(state.parsed_data, "ecmo"):
            ecmo_data = state.parsed_data.ecmo
            if ecmo_data is not None and not ecmo_data.empty:
                ecmo_last_24h = any(
                    (ecmo_data["timestamp"].dt.date == date) |
                    (ecmo_data["timestamp"].dt.date == (date - pd.Timedelta(days=1)))
                )

        # Check for Impella entries on the given date or the day before
        if hasattr(state.parsed_data, "impella"):
            impella_data = state.parsed_data.impella
            if impella_data is not None and not impella_data.empty:
                impella_last_24h = any(
                    (impella_data["timestamp"].dt.date == date) |
                    (impella_data["timestamp"].dt.date == (date - pd.Timedelta(days=1)))
                )

        # Calculate day_of_mcs: days since the first MCS entry (ECMO or Impella)
        min_date = None
        if hasattr(state.parsed_data, "ecmo") and state.parsed_data.ecmo is not None and not state.parsed_data.ecmo.empty:
            ecmo_min = state.parsed_data.ecmo["timestamp"].min()
            if min_date is None or ecmo_min < min_date:
                min_date = ecmo_min
        if hasattr(state.parsed_data, "impella") and state.parsed_data.impella is not None and not state.parsed_data.impella.empty:
            impella_min = state.parsed_data.impella["timestamp"].min()
            if min_date is None or impella_min < min_date:
                min_date = impella_min
        if min_date is not None:
            day_of_mcs = (date - min_date.date()).days + 1
        else:
            day_of_mcs = 0
    else:
        day_of_mcs = 0

    return LabModel(
        date=date,
        **{
            "mcs-last-24": ecmo_last_24h | impella_last_24h,
            "ecls-and-impella-last-24": impella_last_24h & ecmo_last_24h,
            "day_of_mcs": day_of_mcs,
            "withdrawal_site": WithdrawalSite.UNKNOWN,
            "arterial_blood_gas": arterial_blood_gas,
            "date_of_assessment": date,
            "time_of_assessment": date,
            "wbc": get_lab_value(date, "Blutbild", "WBC [K·µL⁻¹]"),
            "hb": get_lab_value(date, "Blutbild", "HB (HGB) [g·dL⁻¹]"),
            "hct": get_lab_value(date, "Blutbild", "HCT [%]"),
            "plt": get_lab_value(date, "Blutbild", "PLT [K·µL⁻¹]"),
            "ptt": get_lab_value(date, "Gerinnung", "PTT [s]"),
            "quick": get_lab_value(date, "Gerinnung", "TPZ [%]"),
            "inr": get_lab_value(date, "Gerinnung", "INR"),
            "act": None,
            "ck": get_lab_value(date, "Enzyme", "CK [U·L⁻¹]"),
            "ck_mb": get_lab_value(date, "Enzyme", "CK-MB [U·L⁻¹]"),
            "ggt": get_lab_value(date, "Enzyme", "GGT [U·L⁻¹]"),
            "ldh": get_lab_value(date, "Enzyme", "LDH [U·L⁻¹]"),
            "lipase": get_lab_value(date, "Enzyme", "LIPASE [U·L⁻¹]"),
            "albumin": None,
            "crp": None,
            "pct": get_lab_value(date, "Klinische Chemie", "PROCALCITONIN [ng·mL⁻¹]"),
            "free_hb": get_lab_value(date, "Blutbild", "FREIES HB [mg·dL⁻¹]"),
            "haptoglobin": None,
            "total_bilirubin": get_lab_value(date, "Klinische Chemie", "BILI (TOT.) [mg·dL⁻¹]"),
            "creatinine": get_lab_value(date, "Klinische Chemie", "KREATININ [mg·dL⁻¹]"),
            "urea": get_lab_value(date, "Klinische Chemie", "HARNSTOFF [mg·dL⁻¹]"),
            "creatinine_clearance": get_lab_value(date, "Klinische Chemie", "GFRKREA [mL·min⁻¹·1.73⁻¹·m⁻²]"),
        }
    )