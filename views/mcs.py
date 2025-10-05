from typing import Optional
import pandas as pd
import streamlit as st

from views.therapy import render_therapy_view


def render_mcs_ecmo(ecmo_df: Optional[pd.DataFrame], key_prefix: str = "mcs_ecmo", start_dt=None, end_dt=None):
    """Render ECMO view via generic therapy renderer."""
    return render_therapy_view(ecmo_df, therapy_label="ECMO", key_prefix=key_prefix, start_dt=start_dt, end_dt=end_dt)


def render_mcs_impella(impella_df: Optional[pd.DataFrame], key_prefix: str = "mcs_impella", start_dt=None, end_dt=None):
    """Render Impella view via generic therapy renderer."""
    return render_therapy_view(impella_df, therapy_label="Impella", key_prefix=key_prefix, start_dt=start_dt, end_dt=end_dt)


def render_mcs(ecmo_df: Optional[pd.DataFrame], impella_df: Optional[pd.DataFrame], key_prefix: str = "mcs", start_dt=None, end_dt=None):
    """Compatibility wrapper that prompts the user to choose ECMO or Impella."""
    st.header("MCS — Auswahl")
    st.info("Bitte wähle im Hauptmenü ECMO oder Impella für detaillierte Ansichten.")
