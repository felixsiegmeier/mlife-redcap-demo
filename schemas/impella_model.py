from pydantic import BaseModel, Field
from typing import Optional, Union
from datetime import datetime


class ImpellaModel(BaseModel):
    timestamp: datetime = Field(..., description="Timestamp of the measurement")
    category: Optional[str] = Field(None, description="Which device if multiple")
    parameter: Optional[str] = Field(None, description="Parameter name")
    value: Optional[Union[float, str]] = Field(None, description="Value of the measurement")
    unit: Optional[str] = Field(None, description="Unit of the measurement")

    class Config:
        orm_mode = True
