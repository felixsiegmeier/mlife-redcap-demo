from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Ecmo(BaseModel):
    timestamp: datetime = Field(..., description="Zeitpunkt der Messung")
    category: Optional[str] = Field(None, description="Bei mehrere: welches Gerät")
    parameter: Optional[str] = Field(None, description="Parameter")
    value: Optional[str | float] = Field(None, description="Wert der Messung")
    unit: Optional[str] = Field(None, description="Einheit der Messung")