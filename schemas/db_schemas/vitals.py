from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime


class NirsLocation(str, Enum):
    CEREBRAL = "cerebral"
    FEMORAL = "femoral"

class NirsValue(BaseModel):
    cerebral_left: Optional[float] = Field(None, description="Cerebral left NIRS value")
    cerebral_right: Optional[float] = Field(None, description="Cerebral right NIRS value")
    femoral_left: Optional[float] = Field(None, description="Femoral left NIRS value")
    femoral_right: Optional[float] = Field(None, description="Femoral right NIRS value")

class NirsModel(BaseModel):
    location: Optional[list[NirsLocation]] = Field(None, description="Location of NIRS measurement")
    nirs_values: Optional[NirsValue] = Field(None, description="NIRS Value")
    change_last_24h: bool = Field(False, description="Change in last 24 hours")
    change: Optional[float] = Field(None, description="Change in NIRS value")

class PacModel(BaseModel):
    pcwp: Optional[float] = Field(None, description="Pulmonary capillary wedge pressure")
    spap: Optional[float] = Field(None, description="Pulmonary artery pressure")
    dpap: Optional[float] = Field(None, description="Pulmonary artery diastolic pressure")
    mpap: Optional[float] = Field(None, description="Pulmonary artery mean pressure")
    ci: Optional[float] = Field(None, description="Cardiac index")

class HemodynamicsModel(BaseModel):
    heart_rate: float = Field(..., description="Heart rate")
    systolic_blood_pressure: float = Field(..., description="Systolic blood pressure")
    diastolic_blood_pressure: float = Field(..., description="Diastolic blood pressure")
    mean_arterial_pressure: float = Field(..., description="Mean arterial pressure")
    central_venous_pressure: float = Field(..., description="Central venous pressure")
    spO2: float = Field(..., description="Peripheral capillary oxygen saturation")
    pac: PacModel | None = Field(None, description="Pulmonary artery catheter")

class VasoactiveAgentsModel(BaseModel):
    norepinephrine: Optional[bool] = Field(default=False, description="Norepinephrine administered")
    epinephrine: Optional[bool] = Field(default=False, description="Epinephrine administered")
    dopamine: Optional[bool] = Field(default=False, description="Dopamine administered")
    dobutamine: Optional[bool] = Field(default=False, description="Dobutamine administered")
    vasopressin: Optional[bool] = Field(default=False, description="Vasopressin administered")
    enoximone: Optional[bool] = Field(default=False, description="Enoximone administered")
    esmolol: Optional[bool] = Field(default=False, description="Esmolol administered")
    levosimendan: Optional[bool] = Field(default=False, description="Levosimendan administered")
    metaraminol: Optional[bool] = Field(default=False, description="Metaraminol administered")
    metoprolol: Optional[bool] = Field(default=False, description="Metoprolol administered")
    milrinone: Optional[bool] = Field(default=False, description="Milrinone administered")
    nicardipine: Optional[bool] = Field(default=False, description="Nicardipine administered")
    nitroglycerin: Optional[bool] = Field(default=False, description="Nitroglycerin administered")
    nitroprusside: Optional[bool] = Field(default=False, description="Nitroprusside administered")
    phenylephrine: Optional[bool] = Field(default=False, description="Phenylephrine administered")
    tolazoline: Optional[bool] = Field(default=False, description="Tolazoline administered")
    empressin: Optional[bool] = Field(default=False, description="Empressin administered")
    dobutamine_dose: Optional[float] = Field(None, description="Dobutamine dosage")
    epinephrine_dose: Optional[float] = Field(None, description="Epinephrine dosage")
    norepinephrine_dose: Optional[float] = Field(None, description="Norepinephrine dosage")
    milrinone_dose: Optional[float] = Field(None, description="Milrinone dosage")
    vasopressin_dose: Optional[float] = Field(None, description="Vasopressin dosage")
    empressin_dose: Optional[float] = Field(None, description="Empressin dosage")
    
class VentilationType(str, Enum):
    INVASIVE = "Invasive Ventilation"
    NON_INVASIVE = "Non invasive Ventilation"
    HIGH_FLOW = "High Flow Therapy"
    NO_VENTILATION = "No Ventilation"

class VentilationSpecifics(str, Enum):
    IPPV = "IPPV"
    BIPAP = "BIPAP"
    SIMV = "SIMV"
    ASB = "ASB"
    PC_BIPAP = "PC-BIPAP"
    PC_PSV = "PC-PSV"
    PC_CMV = "PC-CMV"
    PC_SIMV = "PC-SIMV"
    PC_PC_APRV = "PC-PC-APRV"
    PC_AC = "PC-AC"
    VC_CMV = "VC-CMV"
    VC_SIMV = "VC-SIMV"
    VC_MMV = "VC-MMV"
    VC_AC = "VC-AC"
    SPN_CPAP_PS = "SPN-CPAP/PS"
    BILEVEL = "BiLevel"
    A_C_VC = "A/C VC"
    A_C_PC = "A/C PC"
    A_C_PRVC = "A/C PRVC"
    SIMV_VC = "SIMV-VC"
    SIMV_PC = "SIMV-PC"
    BILEVEL_VG = "BiLevel-VG"
    CPAP_PS = "CPAP/PS"
    SBT = "SBT"
    NIV = "NIV"

class VentilationMode(str, Enum):
    CONVENTIONAL = "Conventional"
    HFO = "HFO"

class VentilationModel(BaseModel):
    ventilation_type: Optional[VentilationType] = Field(None, description="Type of ventilation")
    o2: Optional[float] = Field(None, description="O2 flow rate (L/min)")
    fio2: Optional[float] = Field(None, description="FiO2 (%)")
    ventilation_specifics: Optional[VentilationSpecifics] = Field(None, description="Specific ventilation mode")
    ventilation_mode: Optional[VentilationMode] = Field(None, description="Ventilation mode")
    hfo_ventilation_rate: Optional[float] = Field(None, description="HFO ventilation rate")
    conventional_ventilation_rate: Optional[float] = Field(None, description="Conventional ventilation rate")
    mean_airway_pressure: Optional[float] = Field(None, description="Mean airway pressure (mbar)")
    peak_inspiratory_pressure: Optional[float] = Field(None, description="Peak inspiratory pressure (mbar)")
    positive_end_expiratory_pressure: Optional[float] = Field(None, description="Positive end-expiratory pressure (mbar)")
    prone_position: Optional[bool] = Field(None, description="Prone position")

class MobilizationLevel(str, Enum):
    NOTHING = "Nothing (lying in bed)"
    SITTING_IN_BED = "Sitting in bed, exercises in bed"
    PASSIVELY_MOVED = "Passively moved to chair (no Standing)"
    SITTING_OVER_EDGE = "Sitting over edge of bed"
    STANDING = "Standing (with or without assist)"
    TRANSFERRING = "Transferring bed to chair"
    MARCHING = "Marching on spot (at bedside)"
    WALKING_TWO_PEOPLE = "Walking with assistance of 2 or more People"
    WALKING_ONE_PERSON = "Walking with assistance of 1 Person"
    WALKING_GAIL_AID = "Walking independently with a gail aid"
    WALKING_INDEPENDENTLY = "Walking independently without a gail aid"

class NeurologyModel(BaseModel):
    rass_score: Optional[int] = Field(None, ge=-5, le=4, description="RASS score")
    glasgow_coma_scale: Optional[int] = Field(None, ge=3, le=15, description="Glasgow Coma Scale")
    mobilization_level: Optional[MobilizationLevel] = Field(None, description="Level of Mobilization during ECLS")

class AnticoagulationAgent(str, Enum):
    HEPARIN = "Heparin"
    ARGATROBAN = "Argatroban"

class AntiPlateletAgent(str, Enum):
    ASPIRIN = "Aspirin"
    CLOPIDOGREL = "Clopidogrel"
    TICAGRELOR = "Ticagrelor"
    PRASUGREL = "Prasugrel"

class AnticoagulationModel(BaseModel):
    iv_anticoagulation: bool = Field(False, description="IV Anticoagulation administered")
    iv_anticoagulation_agent: Optional[AnticoagulationAgent] = Field(None, description="IV Anticoagulation agent")
    anti_platelet_therapy: Optional[bool] = Field(None, description="Anti-platelet therapy administered")
    anti_platelet_agents: Optional[list[AntiPlateletAgent]] = Field(None, description="Anti-platelet agents")

class Antibiotic(str, Enum):
    CIPROFLOXACIN = "Ciprofloxacin"
    CEFUROXIM = "Cefuroxim"
    CEFAZOLIN = "Cefazolin"
    CEFTRIAXON = "Ceftriaxon"
    PIPERACILLIN_TAZOBACTAM = "Piperacillin/Tazobactam"
    MEROPENEM = "Meropenem"
    VANCOMYCIN_IV = "Vancomycin i.v."
    VANCOMYCIN_PO = "Vancomycin p.o."
    LINEZOLID = "Linezolid"
    DAPTOMYCIN = "Daptomycin"
    PENICILLIN_G = "Penicillin G"
    FLUCLOXACILLIN = "Flucloxacillin"
    RIFAMPICIN = "Rifampicin"
    GENTAMYCIN = "Gentamycin"
    TOBRAMYCIN = "Tobramycin"
    ERYTHROMYCIN = "Erythromycin"
    CASPOFUNGIN = "Caspofungin"
    AMPHOTERICIN_B_INH = "Amphotericin B inh."
    METRONIDAZOL = "Metronidazol"

class AntimicrobialTreatmentModel(BaseModel):
    antibiotic_antimycotic_treatment: Optional[bool] = Field(None, description="Antibiotic/Antimycotic Treatment administered")
    specific_antibiotic_treatment: Optional[list[Antibiotic]] = Field(None, description="Specific antibiotic treatments")
    antiviral_treatment: Optional[bool] = Field(None, description="Antiviral Treatment administered")
    specific_antiviral_treatment: Optional[str] = Field(None, description="Specific antiviral treatment")

class NutritionType(str, Enum):
    ENTERAL = "Enteral"
    PARENTERAL = "Parenteral"

class NutritionModel(BaseModel):
    nutrition_administered: Optional[bool] = Field(None, description="Nutrition administered")
    specific_nutrition: Optional[list[NutritionType]] = Field(None, description="Specific nutrition type")

class TransfusionModel(BaseModel):
    transfusion_required: Optional[bool] = Field(None, description="Transfusion or Coagulation Products required")
    thrombocyte_transfusion: Optional[float] = Field(None, description="Thrombocyte Transfusion (units/24 hours)")
    red_blood_cell_transfusion: Optional[float] = Field(None, description="Red Blood Cell Transfusion (units/24 hours)")
    fresh_frozen_plasma_transfusion: Optional[float] = Field(None, description="Fresh Frozen Plasma Transfusion (units/24 hours)")
    ppsb_administration: Optional[float] = Field(None, description="PPSB Administration (IU/24h)")
    fibrinogen_administration: Optional[float] = Field(None, description="Fibrinogen Administration (g/24h)")
    antithrombin_iii_administration: Optional[float] = Field(None, description="Antithrombin III Administration (IU/24h)")
    factor_xiii_administration: Optional[float] = Field(None, description="Factor XIII Administration (IU/24h)")

class OtherOrganSupport(str, Enum):
    INHALED_ANESTHETIC = "Inhaled Anesthetic"
    INHALED_EPOPROSTENOL = "Inhaled Epoprostenol"
    INHALED_NITRIC_OXIDE = "Inhaled Nitric Oxide"
    LIQUID_VENTILATION = "Liquid Ventilation"
    SURFACTANT = "Surfactant"
    PLASMAPHERESIS = "Plasmapheresis"
    THERAPEUTIC_HYPOTHERMIA = "Therapeutic Hypothermia < 35°C"
    MARS = "MARS"
    CYTOSORB = "Cytosorb"
    NONE = "None"

class Medication(str, Enum):
    ALPROSTADIL = "Alprostadil"
    IV_BICARBONATE = "IV Bicarbonate"
    PROSTACYCLIN_ANALOGUES = "Prostacyclin Analogues"
    NARCOTICS_SEDATIVE_AGENTS = "Narcotics/Sedative Agents"
    NEUROMUSCULAR_BLOCKERS = "Neuromuscular blockers"
    OPIOIDS = "Opioids"
    ANTIPSYCHOTIC_MEDICATION = "Antipsychotic medication"
    SILDENAFIL = "Sildenafil"
    SYSTEMIC_STEROIDS = "Systemic Steroids"
    TROMETAMOL = "Trometamol"
    NONE = "None"

class NarcoticsSedative(str, Enum):
    PROPOFOL = "Propofol"
    MIDAZOLAM = "Midazolam"
    KETAMIN = "Ketamin"
    DEXMETOMIDIN = "Dexmetomidin"

class OrganSupportModel(BaseModel):
    other_organ_support: Optional[list[OtherOrganSupport]] = Field(None, description="Other organ support methods")
    medication: Optional[list[Medication]] = Field(None, description="Medications for organ support")
    narcotics_sedative_agents: Optional[list[NarcoticsSedative]] = Field(None, description="Narcotics and sedative agents")

class RenalReplacementTherapy(str, Enum):
    HEMODIALYSIS = "Hemodialysis"
    CONTINUOUS_HEMOFILTRATION = "Continuous Hemofiltration"
    NO = "No"

class AcuteKidneyInjury(str, Enum):
    FAILURE = "3 = Failure"

class FluidBalancing(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"

class KidneyFunctionModel(BaseModel):
    renal_replacement_therapy: Optional[RenalReplacementTherapy] = Field(None, description="Renal Replacement Therapy required")
    total_urine_output: Optional[float] = Field(None, description="Total Urine Output")
    acute_kidney_injury: Optional[AcuteKidneyInjury] = Field(None, description="Acute Kidney Injury")
    total_output_renal_replacement: Optional[float] = Field(None, description="Total Output via Renal Replacement Therapy (ml)")
    fluid_balancing_type: Optional[FluidBalancing] = Field(None, description="Fluid Balancing type")
    fluid_balancing: Optional[float] = Field(None, description="Fluid Balancing")

class VitalsModel(BaseModel):
    date: datetime = Field(..., description="Date of the measurement")
    mcs_last_24h: bool = Field(..., alias="mcs-last-24", description="MCS last 24 hours")
    ecls_and_impella_last_24h: bool = Field(..., alias="ecls-and-impella-last-24", description="ECLS and Impella last 24 hours")
    day_of_mcs: int = Field(..., description="Day of MCS")
    nirs: NirsModel | None = Field(None, description="NIRS measurement data")
    hemodynamics: HemodynamicsModel | None = Field(None, description="Hemodynamics measurement data")
    vasoactive_agents: VasoactiveAgentsModel | None = Field(None, description="Vasoactive agents and their dosages")
    ventilation: VentilationModel | None = Field(None, description="Ventilation measurement data")
    neurology: NeurologyModel | None = Field(None, description="Neurology measurement data")
    anticoagulation: AnticoagulationModel | None = Field(None, description="Anticoagulation measurement data")
    antimicrobial_treatment: AntimicrobialTreatmentModel | None = Field(None, description="Antimicrobial treatment data")
    nutrition: NutritionModel | None = Field(None, description="Nutrition data")
    transfusion: TransfusionModel | None = Field(None, description="Transfusion and coagulation products data")
    organ_support: OrganSupportModel | None = Field(None, description="Organ support data")
    kidney_function: KidneyFunctionModel | None = Field(None, description="Kidney function data")
    
    
    class Config:
        from_attributes = True