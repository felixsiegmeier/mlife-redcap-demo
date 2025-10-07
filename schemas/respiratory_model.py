from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class RespiratoryModel(BaseModel):
    timestamp: datetime = Field(..., description="Timestamp of the measurement")
    category: Optional[str] = Field(None, description="Subcategory of the measurement")
    parameter: Optional[str] = Field(None, description="Parameter name")
    value: Optional[float] = Field(None, description="Value of the measurement")

    class Config:
        orm_mode = True
