from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

"""
Blutersatz Konzentration App.- form Start/Änderung Stopp Rate(mL/h)
Medikamente Konzentration App.- form Start/Änderung Stopp Rate(mL/h)
Sonden Konzentration App.- form Start/Änderung Stopp Rate(mL/h)
Infusionen Konzentration App.- form Start/Änderung Stopp Rate(mL/h)
Perfusoren Konzentration App.- form Start/Änderung Stopp Rate(mL/h)
"""

class MedicationModel(BaseModel):
    medication: str = Field(..., description="Name of the medication")
    category: Optional[str] = Field(None, description="Subcategory of the measurement")
    application: Optional[str] = Field(..., description="Kind of application")
    start: Optional[datetime] = Field(None, description="Timestamp of application or infusion start/ change")
    stop: Optional[datetime | None] = Field(None, description="Timestamp of infusion stop")
    concentration: Optional[str] = Field(None, description="Concentration of the medication")
    rate: Optional[float | None] = Field(None, description="Infusion rate of the medication")

    class Config:
        from_attributes = True
