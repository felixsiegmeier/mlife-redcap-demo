from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from typing import Iterable, Optional

import pandas as pd

from state_provider.state_provider import get_state
from state_provider.state_provider_class import state_provider
from schemas.db_schemas.vitals import (
    AntiPlateletAgent,
    AnticoagulationModel,
    AntimicrobialTreatmentModel,
    Antibiotic,
    HemodynamicsModel,
    KidneyFunctionModel,
    Medication,
    NarcoticsSedative,
    NeurologyModel,
    NirsModel,
    NirsValue,
    NutritionModel,
    NutritionType,
    OrganSupportModel,
    OtherOrganSupport,
    PacModel,
    TransfusionModel,
    VasoactiveAgentsModel,
    VentilationModel,
    VitalsModel,
)
from services.date_as_datetime import get_date_as_datetime

DEFAULT_FLOAT = 0.0
logger = logging.getLogger(__name__)


def get_vitals_value(
    record_date: date,
    parameter: Optional[str] = None,
    value_strategy: str = "median",
) -> Optional[float]:
    """Return an aggregated vitals value for the given date/category/parameter."""

    state = get_state()
    vitals_df = getattr(getattr(state, "parsed_data", None), "vitals", None)
    if vitals_df is None or vitals_df.empty or not parameter:
        return None

    filtered = vitals_df[
        (vitals_df["timestamp"].dt.date == record_date)
        & (vitals_df["parameter"].str.lower().contains(parameter.lower(), na=False))
    ]

    if filtered.empty:
        return None

    if value_strategy == "median":
        return float(pd.to_numeric(filtered["value"], errors='coerce').median(skipna=True))
    if value_strategy == "mean":
        return float(filtered["value"].mean())
    if value_strategy == "last":
        return float(filtered["value"].iloc[-1])
    if value_strategy == "first":
        return float(filtered["value"].iloc[0])

    logger.warning("Unknown value_strategy '%s' requested – falling back to median", value_strategy)
    return float(pd.to_numeric(filtered["value"], errors='coerce').median(skipna=True))


def create_vitals_entry(record_date: date, value_strategy: str = "median") -> VitalsModel:
    date_as_datetime = get_date_as_datetime(record_date)

    mcs_last_24h = state_provider.has_mcs_records_past_24h(date_as_datetime)
    ecls_and_impella_last_24h = state_provider.has_device_past_24h("ecmo", date_as_datetime) and state_provider.has_device_past_24h("impella", date_as_datetime)
    day_of_mcs = state_provider.get_time_of_mcs(date_as_datetime)

    date_as_datetime = (
        record_date
        if isinstance(record_date, datetime)
        else datetime.combine(record_date, datetime.min.time())
    )

    nirs = _build_nirs() # must be selected manually since naming of positions is inconsistent -> maybe possible with AI
    hemodynamics = _build_hemodynamics(record_date, value_strategy)
    vasoactive_agents = _build_vasoactive_agents(record_date, value_strategy)
    #ventilation = _build_ventilation(record_date, selection)
    #neurology = _build_neurology(record_date, selection)
    #anticoagulation = _build_anticoagulation(record_date, selection)
    #antimicrobial_treatment = _build_antimicrobial_treatment(record_date, selection)
    #nutrition = _build_nutrition(record_date, selection)
    #transfusion = _build_transfusion(record_date, selection)
    #organ_support = _build_organ_support(record_date, selection)
    #kidney_function = _build_kidney_function(record_date, selection)

    return VitalsModel(
        date=date_as_datetime,
        **{
            "mcs-last-24": mcs_last_24h,
            "ecls-and-impella-last-24": ecls_and_impella_last_24h,
            "day_of_mcs": day_of_mcs,
        },
        nirs=nirs,
        hemodynamics=hemodynamics,
        vasoactive_agents=vasoactive_agents,
        ventilation=ventilation,
        neurology=neurology,
        anticoagulation=anticoagulation,
        antimicrobial_treatment=antimicrobial_treatment,
        nutrition=nutrition,
        transfusion=transfusion,
        organ_support=organ_support,
        kidney_function=kidney_function,
    )


def _build_nirs() -> NirsModel:
    nirs_values = NirsValue(
        cerebral_left= 0,
        cerebral_right= 0,
        femoral_left= 0,
        femoral_right= 0,
        )

    return NirsModel(
        location=[],  # TODO: derive actual locations once the source data is mapped
        nirs_values=nirs_values,
        change_last_24h=False,
        change=None,
    )


def _build_hemodynamics(record_date: date, value_strategy: str) -> HemodynamicsModel:
    pac_candidates = {
        "pcwp": _normalize_optional_float(
            get_vitals_value(record_date,"PAWP", value_strategy)
        ),
        "spap": _normalize_optional_float(
            get_vitals_value(record_date, "PAPs", value_strategy)
        ),
        "dpap": _normalize_optional_float(
            get_vitals_value(record_date, "PAPd", value_strategy)
        ),
        "mpap": _normalize_optional_float(
            get_vitals_value(record_date, "PAPm", value_strategy)
        ),
        "ci": _normalize_optional_float(
            get_vitals_value(record_date, "CCI", value_strategy)
        ),
    }

    pac = PacModel(**pac_candidates) if any(value is not None for value in pac_candidates.values()) else None

    return HemodynamicsModel(
        heart_rate=_ensure_float(
            get_vitals_value(record_date, "<TODO:HEMODYNAMICS>", "<TODO:HEART RATE>", value_strategy)
        ),
        systolic_blood_pressure=_ensure_float(
            get_vitals_value(record_date, "<TODO:HEMODYNAMICS>", "<TODO:SYSTOLIC BP>", value_strategy)
        ),
        diastolic_blood_pressure=_ensure_float(
            get_vitals_value(record_date, "<TODO:HEMODYNAMICS>", "<TODO:DIASTOLIC BP>", value_strategy)
        ),
        mean_arterial_pressure=_ensure_float(
            get_vitals_value(record_date, "<TODO:HEMODYNAMICS>", "<TODO:MEAN AP>", value_strategy)
        ),
        central_venous_pressure=_ensure_float(
            get_vitals_value(record_date, "<TODO:HEMODYNAMICS>", "<TODO:CVP>", value_strategy)
        ),
        spO2=_ensure_float(
            get_vitals_value(record_date, "<TODO:HEMODYNAMICS>", "<TODO:SpO2>", value_strategy)
        ),
        pac=pac,
    )


def _build_vasoactive_agents(record_date: date, value_strategy: str) -> VasoactiveAgentsModel:
    date = get_date_as_datetime(record_date)
    
    return VasoactiveAgentsModel(
        norepinephrine= not state_provider.get_vasoactive_agents_df(date, "Norepinephrin").empty,
        epinephrine= not state_provider.get_vasoactive_agents_df(date, "Epinephrin").empty,
        dopamine= not state_provider.get_vasoactive_agents_df(date, "Dopamin").empty,
        dobutamine= not state_provider.get_vasoactive_agents_df(date, "Dobutamin").empty,
        vasopressin= not state_provider.get_vasoactive_agents_df(date, "Vasopressin").empty,
        enoximone= not state_provider.get_vasoactive_agents_df(date, "Enoximon").empty,
        esmolol= not state_provider.get_vasoactive_agents_df(date, "Esmolol").empty,
        levosimendan= not state_provider.get_vasoactive_agents_df(date, "Levosimendan").empty,
        metaraminol= not state_provider.get_vasoactive_agents_df(date, "Metaraminol").empty,
        metoprolol= not state_provider.get_vasoactive_agents_df(date, "Metoprolol").empty,
        milrinone= not state_provider.get_vasoactive_agents_df(date, "Milrinon").empty,
        nicardipine= not state_provider.get_vasoactive_agents_df(date, "Nicardipin").empty,
        nitroglycerin= not state_provider.get_vasoactive_agents_df(date, "Nitroglycerin").empty,
        nitroprusside= not state_provider.get_vasoactive_agents_df(date, "Nitroprussid").empty,
        phenylephrine= not state_provider.get_vasoactive_agents_df(date, "Esmolol").empty,
        tolazoline= not state_provider.get_vasoactive_agents_df(date, "Tolazolin").empty,
        empressin= not state_provider.get_vasoactive_agents_df(date, "Empressin").empty,
        dobutamine_dose= 0,
        epinephrine_dose=0,
        norepinephrine_dose=0,
        milrinone_dose=0,
        vasopressin_dose=0,
        empressin_dose=0
    )


def _build_ventilation(record_date: date, value_strategy: str) -> VentilationModel:
    date = get_date_as_datetime(record_date)
    return VentilationModel(
        ventilation_type : VentilationTyp =None,
    o2=state_provider.get_respiratory_value(date, "FiO2", value_strategy),
    fio2=state_provider.get_respiratory_value(date, "FiO2", value_strategy),
        ventilation_specifics=None,
        ventilation_mode=None,
    hfo_ventilation_rate=state_provider.get_respiratory_value(date, "Spontanatemfrequenz", value_strategy),
    conventional_ventilation_rate=state_provider.get_respiratory_value(date, "Atemfrequenz", value_strategy),
    mean_airway_pressure=state_provider.get_respiratory_value(date, "FiO2", value_strategy),
    peak_inspiratory_pressure=state_provider.get_respiratory_value(date, "FiO2", value_strategy),
    positive_end_expiratory_pressure=state_provider.get_respiratory_value(date, "PEEP", value_strategy),
        prone_position=False
    )


def _build_neurology(record_date: date, value_strategy: str) -> NeurologyModel:
    return NeurologyModel(
        rass_score=_normalize_optional_int(
            get_vitals_value(record_date, "<TODO:NEUROLOGY>", "<TODO:RASS>", value_strategy)
        ),
        glasgow_coma_scale=_normalize_optional_int(
            get_vitals_value(record_date, "<TODO:NEUROLOGY>", "<TODO:GCS>", value_strategy)
        ),
        mobilization_level=None,
    )


def _build_anticoagulation(record_date: date, value_strategy: str) -> AnticoagulationModel:
    return AnticoagulationModel(
        iv_anticoagulation=_ensure_bool(
            get_vitals_value(record_date, "<TODO:ANTICOAGULATION>", "<TODO:IV ANTICOAGULATION>", value_strategy)
        ),
        iv_anticoagulation_agent=None,
        anti_platelet_therapy=_ensure_bool(
            get_vitals_value(record_date, "<TODO:ANTICOAGULATION>", "<TODO:ANTI PLATELET THERAPY>", value_strategy)
        ),
        anti_platelet_agents=_normalize_enum_list(
            _value_to_iterable(
                get_vitals_value(record_date, "<TODO:ANTICOAGULATION>", "<TODO:ANTI PLATELET AGENTS>", value_strategy)
            ),
            enum_cls=AntiPlateletAgent,
        ),
    )


def _build_antimicrobial_treatment(record_date: date, value_strategy: str) -> AntimicrobialTreatmentModel:
    return AntimicrobialTreatmentModel(
        antibiotic_antimycotic_treatment=_ensure_bool(
            get_vitals_value(record_date, "<TODO:ANTIMICROBIAL>", "<TODO:ANTIBIOTIC ANTIMYCOTIC>", value_strategy)
        ),
        specific_antibiotic_treatment=_normalize_enum_list(
            _value_to_iterable(
                get_vitals_value(record_date, "<TODO:ANTIMICROBIAL>", "<TODO:SPECIFIC ANTIBIOTICS>", value_strategy)
            ),
            enum_cls=Antibiotic,
        ),
        antiviral_treatment=_ensure_bool(
            get_vitals_value(record_date, "<TODO:ANTIMICROBIAL>", "<TODO:ANTIVIRAL>", value_strategy)
        ),
        specific_antiviral_treatment=_normalize_optional_str(
            get_vitals_value(record_date, "<TODO:ANTIMICROBIAL>", "<TODO:SPECIFIC ANTIVIRAL>", value_strategy)
        ),
    )


def _build_nutrition(record_date: date, value_strategy: str) -> NutritionModel:
    return NutritionModel(
        nutrition_administered=_ensure_bool(
            get_vitals_value(record_date, "<TODO:NUTRITION>", "<TODO:NUTRITION ADMINISTERED>", value_strategy)
        ),
        specific_nutrition=_normalize_enum_list(
            _value_to_iterable(
                get_vitals_value(record_date, "<TODO:NUTRITION>", "<TODO:SPECIFIC NUTRITION>", value_strategy)
            ),
            enum_cls=NutritionType,
        ),
    )


def _build_transfusion(record_date: date, value_strategy: str) -> TransfusionModel:
    return TransfusionModel(
        transfusion_required=_ensure_bool(
            get_vitals_value(record_date, "<TODO:TRANSFUSION>", "<TODO:TRANSFUSION REQUIRED>", value_strategy)
        ),
        thrombocyte_transfusion=_normalize_optional_float(
            get_vitals_value(record_date, "<TODO:TRANSFUSION>", "<TODO:THROMBOCYTE>", value_strategy)
        ),
        red_blood_cell_transfusion=_normalize_optional_float(
            get_vitals_value(record_date, "<TODO:TRANSFUSION>", "<TODO:RBC>", value_strategy)
        ),
        fresh_frozen_plasma_transfusion=_normalize_optional_float(
            get_vitals_value(record_date, "<TODO:TRANSFUSION>", "<TODO:FFP>", value_strategy)
        ),
        ppsb_administration=_normalize_optional_float(
            get_vitals_value(record_date, "<TODO:TRANSFUSION>", "<TODO:PPSB>", value_strategy)
        ),
        fibrinogen_administration=_normalize_optional_float(
            get_vitals_value(record_date, "<TODO:TRANSFUSION>", "<TODO:FIBRINOGEN>", value_strategy)
        ),
        antithrombin_iii_administration=_normalize_optional_float(
            get_vitals_value(record_date, "<TODO:TRANSFUSION>", "<TODO:ATIII>", value_strategy)
        ),
        factor_xiii_administration=_normalize_optional_float(
            get_vitals_value(record_date, "<TODO:TRANSFUSION>", "<TODO:FACTOR XIII>", value_strategy)
        ),
    )


def _build_organ_support(record_date: date, value_strategy: str) -> OrganSupportModel:
    return OrganSupportModel(
        other_organ_support=_normalize_enum_list(
            _value_to_iterable(
                get_vitals_value(record_date, "<TODO:ORGAN SUPPORT>", "<TODO:OTHER ORGAN SUPPORT>", value_strategy)
            ),
            enum_cls=OtherOrganSupport,
        ),
        medication=_normalize_enum_list(
            _value_to_iterable(
                get_vitals_value(record_date, "<TODO:ORGAN SUPPORT>", "<TODO:MEDICATION>", value_strategy)
            ),
            enum_cls=Medication,
        ),
        narcotics_sedative_agents=_normalize_enum_list(
            _value_to_iterable(
                get_vitals_value(record_date, "<TODO:ORGAN SUPPORT>", "<TODO:NARCOTICS>", value_strategy)
            ),
            enum_cls=NarcoticsSedative,
        ),
    )


def _build_kidney_function(record_date: date, value_strategy: str) -> KidneyFunctionModel:
    return KidneyFunctionModel(
        renal_replacement_therapy=None,
        total_urine_output=_normalize_optional_float(
            get_vitals_value(record_date, "<TODO:KIDNEY>", "<TODO:URINE OUTPUT>", value_strategy)
        ),
        acute_kidney_injury=None,
        total_output_renal_replacement=_normalize_optional_float(
            get_vitals_value(record_date, "<TODO:KIDNEY>", "<TODO:RRT OUTPUT>", value_strategy)
        ),
        fluid_balancing_type=None,
        fluid_balancing=_normalize_optional_float(
            get_vitals_value(record_date, "<TODO:KIDNEY>", "<TODO:FLUID BALANCING>", value_strategy)
        ),
    )


def _compute_mcs_flags(record_date: date) -> tuple[bool, bool]:
    state = get_state()
    parsed = getattr(state, "parsed_data", None)
    if not parsed:
        return False, False

    ecmo_df = getattr(parsed, "ecmo", None)
    impella_df = getattr(parsed, "impella", None)

    ecmo_last_24h = _dataframe_contains_date(ecmo_df, record_date)
    impella_last_24h = _dataframe_contains_date(impella_df, record_date)

    return ecmo_last_24h or impella_last_24h, ecmo_last_24h and impella_last_24h


def _compute_day_of_mcs(record_date: date) -> int:
    state = get_state()
    parsed = getattr(state, "parsed_data", None)
    if not parsed:
        return 0

    min_timestamp: Optional[pd.Timestamp] = None
    for attr in ("ecmo", "impella"):
        df = getattr(parsed, attr, None)
        if df is None or df.empty:
            continue
        candidate = df["timestamp"].min()
        if pd.isna(candidate):
            continue
        if min_timestamp is None or candidate < min_timestamp:
            min_timestamp = candidate

    if min_timestamp is None:
        return 0

    return (record_date - min_timestamp.date()).days + 1


def _dataframe_contains_date(df: Optional[pd.DataFrame], record_date: date) -> bool:
    if df is None or df.empty or "timestamp" not in df.columns:
        return False
    target_dates = {record_date, record_date - timedelta(days=1)}
    return bool(df["timestamp"].dt.date.isin(target_dates).any())


def _ensure_float(value: Optional[float], default: float = DEFAULT_FLOAT) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _normalize_optional_float(value: Optional[float]) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _normalize_optional_int(value: Optional[float]) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(round(float(value)))
    except (TypeError, ValueError):
        return None


def _normalize_optional_str(value: Optional[object]) -> Optional[str]:
    if value is None:
        return None
    return str(value)


def _ensure_bool(value: Optional[float]) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    try:
        return bool(float(value))
    except (TypeError, ValueError):
        return False


def _value_to_iterable(value: Optional[object]) -> list[object]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return list(value)
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return [value]


def _normalize_enum_list(values: Iterable[object], enum_cls) -> list:
    result = []
    for raw in values:
        try:
            result.append(enum_cls(raw) if not isinstance(raw, enum_cls) else raw)
        except ValueError:
            logger.debug("Failed to coerce '%s' into %s", raw, enum_cls.__name__)
    return result

