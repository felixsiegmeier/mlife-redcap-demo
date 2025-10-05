import streamlit as st
from typing import List


def param_checkboxes(params: List[str], key_prefix: str, default_all: bool = True) -> List[str]:
    """
    Rendert in der Sidebar eine 'Select all' Checkbox und für jeden Parameter eine einzelne Checkbox.

    Speichert den Zustand in st.session_state unter eindeutigen Keys (key_prefix + index).
    Gibt die Liste der ausgewählten Parameter zurück.
    """
    if not params:
        return []

    select_all_key = f"{key_prefix}_select_all"
    initialized_key = f"{key_prefix}_initialized"

    # Select all checkbox
    select_all = st.sidebar.checkbox("Alle auswählen / abwählen", value=default_all, key=select_all_key)

    # Initialisiere per-param session state falls noch nicht vorhanden
    if initialized_key not in st.session_state:
        for i, p in enumerate(params):
            k = f"{key_prefix}_param_{i}"
            # set default only if key not present
            if k not in st.session_state:
                st.session_state[k] = default_all
        st.session_state[initialized_key] = True

    # Wenn Select all aktiviert ist, setze alle param-keys entsprechend
    if select_all:
        for i, _ in enumerate(params):
            k = f"{key_prefix}_param_{i}"
            # direkt in session_state schreiben um checkboxen zu aktualisieren
            st.session_state[k] = True

    selected = []
    # Render individual checkboxes
    for i, p in enumerate(params):
        k = f"{key_prefix}_param_{i}"
        # value=... sorgt dafür, dass checkbox den session state initial widerspiegelt
        checked = st.sidebar.checkbox(p, value=st.session_state.get(k, False), key=k)
        # der aktuelle checked Wert ist in st.session_state[k]
        if st.session_state.get(k, False):
            selected.append(p)

    # Speichere die aktuelle Auswahl als Liste unter einem konsistenten Key
    sel_key = f"{key_prefix}_selected"
    st.session_state[sel_key] = selected
    return selected
