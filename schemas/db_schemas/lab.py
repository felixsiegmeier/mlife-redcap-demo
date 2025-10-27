from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date, time
from enum import Enum


class WithdrawalSite(str, Enum):
    ARTERIA_RADIALIS_RIGHT = "radialis_r"
    ARTERIA_RADIALIS_LEFT = "radialis_l"
    ARTERIA_FEMORALIS_RIGHT = "femoralis_r"
    ARTERIA_FEMORALIS_LEFT = "femoralis_l"
    ARTERIA_BRACHIALIS_RIGHT = "brachialis_r"
    ARTERIA_BRACHIALIS_LEFT = "brachialis_l"
    UNKNOWN = "unknown"


class LabModel(BaseModel):
    record_id: str = Field(..., alias="record_id")
    redcap_event_name: str = Field("labor", alias="redcap_event_name")
    redcap_repeat_instrument: Optional[str] = Field(None, alias="redcap_repeat_instrument")
    redcap_repeat_instance: Optional[int] = Field(None, alias="redcap_repeat_instance")

    # Zeitpunkt/Erhebungsmetadaten
    assess_time_point_labor: Optional[str] = Field(None, alias="assess_time_point_labor")
    assess_date_labor: Optional[date] = Field(None, alias="assess_date_labor")
    date_assess_labor: Optional[date] = Field(None, alias="date_assess_labor")
    time_assess_labor: Optional[time] = Field(None, alias="time_assess_labor")

    art_site: WithdrawalSite = Field(WithdrawalSite.UNKNOWN, alias="art_site")

    # Blutgas-Parameter
    pco2: Optional[float] = Field(None, alias="pc02")
    po2: Optional[float] = Field(None, alias="p02")
    ph: Optional[float] = Field(None, alias="ph")
    hco3: Optional[float] = Field(None, alias="hco3")
    be: Optional[float] = Field(None, alias="be")
    sao2: Optional[float] = Field(None, alias="sa02")
    kalium: Optional[float] = Field(None, alias="k")
    natrium: Optional[float] = Field(None, alias="na")
    glucose: Optional[float] = Field(None, alias="gluc")
    lactate: Optional[float] = Field(None, alias="lactate")
    svo2: Optional[float] = Field(None, alias="sv02")

    # Hämatologie & Gerinnung
    wbc: Optional[float] = Field(None, alias="wbc")
    hb: Optional[float] = Field(None, alias="hb")
    hct: Optional[float] = Field(None, alias="hct")
    plt: Optional[float] = Field(None, alias="plt")
    ptt: Optional[float] = Field(None, alias="ptt")
    quick: Optional[float] = Field(None, alias="quick")
    inr: Optional[float] = Field(None, alias="inr")
    post_act: Optional[float] = Field(None, alias="post_act")
    act: Optional[float] = Field(None, alias="act")

    # Organsystem-Labore
    ck: Optional[float] = Field(None, alias="ck")
    ckmb: Optional[float] = Field(None, alias="ckmb")
    got: Optional[float] = Field(None, alias="got")
    alat: Optional[float] = Field(None, alias="alat")
    ggt: Optional[float] = Field(None, alias="ggt")
    ldh: Optional[float] = Field(None, alias="ldh")
    lipase: Optional[float] = Field(None, alias="lipase")
    albumin: Optional[float] = Field(None, alias="albumin")
    post_crp: Optional[float] = Field(None, alias="post_crp")
    crp: Optional[float] = Field(None, alias="crp")
    post_pct: Optional[float] = Field(None, alias="post_pct")
    pct: Optional[float] = Field(None, alias="pct")
    hemolysis: Optional[float] = Field(None, alias="hemolysis")
    free_hb: Optional[float] = Field(None, alias="fhb")
    haptoglobin: Optional[float] = Field(None, alias="hapto")
    total_bilirubin: Optional[float] = Field(None, alias="bili")
    creatinine: Optional[float] = Field(None, alias="crea")
    creatinine_clearance: Optional[float] = Field(None, alias="cc")
    urea: Optional[float] = Field(None, alias="urea")

    labor_complete: Optional[int] = Field(None, alias="labor_complete")

    class Config:
        populate_by_name = True
        from_attributes = True