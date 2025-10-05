import streamlit as st
import pandas as pd
from typing import List, Optional


def render_overview(key_prefixes: Optional[List[str]] = None) -> None:
    """
    Sammle alle per-View ausgewählten Parameter (gespeichert in session_state under '<prefix>_selected')
    und zeige eine kombinierte Tabelle. Füge einen Demo-Button für API-Export hinzu (Platzhalter).
    """
    st.header("Übersicht — ausgewählte Parameter")

    # Sammle alle Keys in session_state, die auf '_params' enden (Multiselect-Keys)
    rows = []
    for k, v in st.session_state.items():
        if not isinstance(k, str):
            continue
        if k.endswith('_params') and isinstance(v, (list, tuple)) and v:
            # bestimme eine lesbare view-bezeichnung aus dem key (bis zum ersten '_params')
            view_name = k[:-7]
            for p in v:
                rows.append({"view": view_name, "parameter": p})

    if not rows:
        st.info("Keine Parameter ausgewählt. Wähle per Views in der Sidebar Parameter aus.")
        return

    df = pd.DataFrame(rows)
    st.write(df)

    # Demo / Platzhalter Button für API-Export
    if st.button("API-Export (Demo)"):
        st.info("API-Export ausgelöst (Demo-Button, noch ohne Implementierung)")
