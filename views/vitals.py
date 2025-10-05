from typing import Optional
import pandas as pd

from views.numeric_view import render_numeric_view


def render_vitals(df: Optional[pd.DataFrame], label: str = "Vitaldaten", key_prefix: str = "df1_vitals", start_dt=None, end_dt=None):
    """Compatibility wrapper for vitals view — delegates to generic numeric renderer."""
    return render_numeric_view(df, label=label, key_prefix=key_prefix, start_dt=start_dt, end_dt=end_dt)

