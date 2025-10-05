from typing import Optional
import pandas as pd

from views.numeric_view import render_numeric_view


def render_lab(df: Optional[pd.DataFrame], label: str = "Labor", key_prefix: str = "df3_lab", start_dt=None, end_dt=None):
    """Compatibility wrapper for lab view — delegates to generic numeric renderer."""
    return render_numeric_view(df, label=label, key_prefix=key_prefix, start_dt=start_dt, end_dt=end_dt)
