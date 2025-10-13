from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime


class WithdrawalSite(str, Enum):
    ARTERIA_RADIALIS_RIGHT = "Arteria radialis right"
    ARTERIA_RADIALIS_LEFT = "Arteria radialis left"
    ARTERIA_BRACHIALIS_RIGHT = "Arteria brachialis right"
    ARTERIA_BRACHIALIS_LEFT = "Arteria brachialis left"
    ARTERIA_FEMORALIS_RIGHT = "Arteria femoralis right"
    ARTERIA_FEMORALIS_LEFT = "Arteria femoralis left"
    UNKNOWN = "unknown"

class ArterialBloodGasModel(BaseModel):
    pco2: Optional[float] = Field(None, description="pCO2 (mmHg)")
    po2: Optional[float] = Field(None, description="pO2 (mmHg)")
    ph: Optional[float] = Field(None, description="pH")
    hco3: Optional[float] = Field(None, description="HCO3 (mmol/L)")
    be: Optional[float] = Field(None, description="BE (mmol/L)")
    sao2: Optional[float] = Field(None, description="SaO2 (%)")
    kalium: Optional[float] = Field(None, description="Kalium (mmol/L)")
    natrium: Optional[float] = Field(None, description="Natrium (mmol/L)")
    glucose: Optional[float] = Field(None, description="Glucose (mg/dL)")
    lactate: Optional[float] = Field(None, description="Lactate (mg/dL)")
    svo2: Optional[float] = Field(None, description="SvO2 (%)")

class LabModel(BaseModel):
    date: datetime = Field(..., description="Timestamp of the measurement")
    mcs_last_24h: bool = Field(..., alias="mcs-last-24", description="MCS last 24 hours")
    ecls_and_impella_last_24h: bool = Field(..., alias="ecls-and-impella-last-24", description="ECLS and Impella last 24 hours")
    date: datetime = Field(..., description="Date of the measurement")
    day_of_mcs: int = Field(..., description="Day of MCS")
    withdrawal_site: WithdrawalSite = Field(WithdrawalSite.UNKNOWN, description="withdrawal site of arterial blood")
    arterial_blood_gas: ArterialBloodGasModel = Field(..., description="Arterial blood gas values")
    date_of_assessment: datetime = Field(..., description="Date of assessment")
    time_of_assessment: datetime = Field(..., description="Time of assessment")
    wbc: Optional[float] = Field(None, description="White blood cell count (10^9/L)")
    hb: Optional[float] = Field(None, description="Hemoglobin (g/dL)")
    hct: Optional[float] = Field(None, description="Hematocrit (%)")
    plt: Optional[float] = Field(None, description="Platelet count (10^9/L)")
    ptt: Optional[float] = Field(None, description="Partial thromboplastin time (seconds)")
    quick: Optional[float] = Field(None, description="Prothrombin time in %")
    inr: Optional[float] = Field(None, description="International normalized ratio (INR)")
    act: Optional[float] = Field(None, description="Activated clotting time (seconds)")
    ck: Optional[float] = Field(None, description="Creatine kinase (U/L)")
    ck_mb: Optional[float] = Field(None, description="Creatine kinase MB (U/L)")
    ggt: Optional[float] = Field(None, description="Gamma-glutamyl transferase (U/L)")
    ldh: Optional[float] = Field(None, description="Lactate dehydrogenase (U/L)")
    lipase: Optional[float] = Field(None, description="Lipase (U/L)")
    albumin: Optional[float] = Field(None, description="Albumin (g/dL)")
    crp: Optional[float] = Field(None, description="C-reactive protein (mg/L)")
    pct: Optional[float] = Field(None, description="Procalcitonin (ng/mL)")
    free_hb: Optional[float] = Field(None, description="Free hemoglobin (mg/dL)")
    haptoglobin: Optional[float] = Field(None, description="Haptoglobin (mg/dL)")
    total_bilirubin: Optional[float] = Field(None, description="Total bilirubin (mg/dL)")
    creatinine: Optional[float] = Field(None, description="Creatinine (mg/dL)")
    urea: Optional[float] = Field(None, description="Urea (mg/dL)")
    creatinine_clearance: Optional[float] = Field(None, description="Creatinine clearance (mL/min)")

    class Config:
        orm_mode = True