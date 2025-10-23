from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FluidBalanceModel(BaseModel):
    timestamp: Optional[datetime]
    value: float
    category: str  # e.g., "Ausfuhr Flüss.", "Einfuhr Flüss."
    parameter: str  # e.g., "Dialyse", "Infusion"
    time_range: Optional[str]  # e.g., "10.09.2025 11:00 - 15.09.2025 07:59"