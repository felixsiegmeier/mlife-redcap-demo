import pandas as pd
import streamlit as st
from typing import Optional
from views._ui import param_checkboxes
from views.therapy import render_therapy_view


def render_rrt(crrt_df, key_prefix: str = "rrt", start_dt=None, end_dt=None):
    return render_therapy_view(crrt_df, therapy_label="RRT / Hämofilter", key_prefix=key_prefix, start_dt=start_dt, end_dt=end_dt)
    return df.copy()
