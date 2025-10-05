import streamlit as st
import pandas as pd
from typing import Optional


def _coerce_series(x):
    if isinstance(x, pd.Series):
        return x
    try:
        return pd.Series(x)
    except Exception:
        return pd.Series([], dtype=object)


def _safe_key(base: str) -> str:
    # convert arbitrary option text to a safe widget key fragment
    return "".join([c if c.isalnum() else "_" for c in str(base)])


def _render_checkbox_grid(container, options, list_key: str, ncols: int = 2):
    """Render options as a grid of checkboxes inside the given container.

    Persists the selected options in st.session_state[list_key] (list of values).
    Each underlying checkbox uses its own key derived from list_key and the
    option text so Streamlit remembers individual checkbox state across reruns.
    """
    if not options:
        container.info("Keine Optionen vorhanden")
        st.session_state.setdefault(list_key, [])
        return []

    inited_key = f"{list_key}__inited"
    # initialize per-checkbox keys once (do not reset on every rerun)
    if not st.session_state.get(inited_key, False):
        st.session_state.setdefault(list_key, [])
        for opt in options:
            chk_key_init = f"{list_key}__chk__{_safe_key(opt)}"
            # explicitly set to False to avoid old True states
            st.session_state[chk_key_init] = False
        st.session_state[inited_key] = True

    cols = container.columns(ncols)
    for i, opt in enumerate(options):
        col = cols[i % ncols]
        chk_key = f"{list_key}__chk__{_safe_key(opt)}"
        default = True if (st.session_state.get(list_key) and opt in st.session_state.get(list_key)) else False
        with col:
            # create checkbox inside the provided container
            container.checkbox(str(opt), value=default, key=chk_key)

    # collect selection from individual checkbox keys and store as list
    selected = [opt for opt in options if st.session_state.get(f"{list_key}__chk__{_safe_key(opt)}", False)]
    st.session_state[list_key] = selected
    return selected


def render_selection_panel(df_1: Optional[pd.DataFrame], df_2: Optional[pd.DataFrame], df_3: Optional[pd.DataFrame], ecmo_df: Optional[pd.DataFrame], impella_df: Optional[pd.DataFrame], crrt_df: Optional[pd.DataFrame]):
    """Render a persistent selection panel in the sidebar.

    This creates expanders for each data source with multiselects and average-checkboxes.
    Widgets are given stable keys so their state persists across view changes.
    """
    st.sidebar.markdown("### Auswahl — persistent")

    # small control to clear saved selections (use when old session state kept checkboxes checked)
    if st.sidebar.button("Reset Auswahl (Checkboxen)"):
        keys = list(st.session_state.keys())
        keys_to_remove = [k for k in keys if ("__chk__" in str(k)) or str(k).endswith("_params") or str(k).endswith("_devices") or str(k).endswith("_avg")]
        for k in keys_to_remove:
            try:
                del st.session_state[k]
            except Exception:
                # ignore deletion errors
                pass
        st.sidebar.success("Auswahl zurückgesetzt — Seite neu laden, falls nötig.")

    # Vitals
    with st.sidebar.expander("Vitals (Vitaldaten)", expanded=False):
        if df_1 is None or df_1.empty:
            st.info("Keine Vitaldaten im Upload gefunden.")
        else:
            ser = _coerce_series(df_1['parameter']) if 'parameter' in df_1.columns else pd.Series([], dtype=object)
            opts = sorted(ser.dropna().unique().tolist())
            key_params = "df1_vitals_params"
            # rely on session_state via the widget key to persist selection;
            # avoid passing `default=` which can overwrite session_state on reruns
            # render as checkbox grid to save vertical space and preserve session_state
            _render_checkbox_grid(st, opts, key_params, ncols=2)
            st.checkbox("Tägliche Mittelwerte (Vitals)", value=st.session_state.get("df1_vitals_avg", False), key="df1_vitals_avg")

    # Respirator
    with st.sidebar.expander("Respirator (Respiratordaten)", expanded=False):
        if df_2 is None or df_2.empty:
            st.info("Keine Respiratordaten im Upload gefunden.")
        else:
            ser = _coerce_series(df_2['parameter']) if 'parameter' in df_2.columns else pd.Series([], dtype=object)
            opts = sorted(ser.dropna().unique().tolist())
            key_params = "df2_resp_params"
            _render_checkbox_grid(st, opts, key_params, ncols=2)
            st.checkbox("Tägliche Mittelwerte (Respirator)", value=st.session_state.get("df2_resp_avg", False), key="df2_resp_avg")

    # Labor
    with st.sidebar.expander("Labor", expanded=False):
        if df_3 is None or df_3.empty:
            st.info("Keine Labordaten im Upload gefunden.")
        else:
            ser = _coerce_series(df_3['parameter']) if 'parameter' in df_3.columns else pd.Series([], dtype=object)
            opts = sorted(ser.dropna().unique().tolist())
            key_params = "df3_lab_params"
            _render_checkbox_grid(st, opts, key_params, ncols=2)
            st.checkbox("Tägliche Mittelwerte (Labor)", value=st.session_state.get("df3_lab_avg", False), key="df3_lab_avg")

    # MCS: separate sections for ECMO and Impella (support multi-device selection)
    with st.sidebar.expander("MCS — ECMO", expanded=False):
        if ecmo_df is None or ecmo_df.empty:
            st.info("Keine ECMO-Daten im Upload gefunden.")
        else:
            ser_devs = pd.Series([], dtype=object)
            if ecmo_df is not None and 'Sub-Kategorie' in ecmo_df.columns:
                ser_devs = _coerce_series(ecmo_df['Sub-Kategorie'])
            devices = sorted(ser_devs.dropna().unique().tolist())
            if devices:
                key_devices = "mcs_ecmo_devices"
                selected_devices = st.multiselect("ECMO — Geräte auswählen (Mehrfach)", options=devices, key=key_devices)

                # Shared parameter filter for all selected ECMO devices
                if 'Parameter' in ecmo_df.columns:
                    ser_params = _coerce_series(ecmo_df['Parameter'])
                    all_opts = sorted(ser_params.dropna().unique().tolist())
                else:
                    all_opts = []
                keyp = "mcs_ecmo_params"
                _render_checkbox_grid(st, all_opts, keyp, ncols=2)
                st.checkbox("Tägliche Mittelwerte — ECMO (für alle Geräte)", value=st.session_state.get("mcs_ecmo_avg", False), key="mcs_ecmo_avg")
            else:
                st.info("Keine Geräte/Sub-Kategorien für ECMO gefunden")

    with st.sidebar.expander("MCS — Impella", expanded=False):
        if impella_df is None or impella_df.empty:
            st.info("Keine Impella-Daten im Upload gefunden.")
        else:
            ser_devs = pd.Series([], dtype=object)
            if impella_df is not None and 'Sub-Kategorie' in impella_df.columns:
                ser_devs = _coerce_series(impella_df['Sub-Kategorie'])
            devices = sorted(ser_devs.dropna().unique().tolist())
            if devices:
                key_devices = "mcs_impella_devices"
                selected_devices = st.multiselect("Impella — Geräte auswählen (Mehrfach)", options=devices, key=key_devices)

                # Shared parameter filter for all selected Impella devices
                if 'Parameter' in impella_df.columns:
                    ser_params = _coerce_series(impella_df['Parameter'])
                    all_opts = sorted(ser_params.dropna().unique().tolist())
                else:
                    all_opts = []
                keyp = "mcs_impella_params"
                _render_checkbox_grid(st, all_opts, keyp, ncols=2)
                st.checkbox("Tägliche Mittelwerte — Impella (für alle Geräte)", value=st.session_state.get("mcs_impella_avg", False), key="mcs_impella_avg")
            else:
                st.info("Keine Geräte/Sub-Kategorien für Impella gefunden")

    # RRT
    with st.sidebar.expander("RRT / Hämofilter", expanded=False):
        if crrt_df is None or crrt_df.empty:
            st.info("Keine RRT-Daten im Upload gefunden.")
        else:
            ser_devs = pd.Series([], dtype=object)
            if crrt_df is not None and 'Sub-Kategorie' in crrt_df.columns:
                ser_devs = _coerce_series(crrt_df['Sub-Kategorie'])
            devices = sorted(ser_devs.dropna().unique().tolist())
            if devices:
                # select devices
                key_devices = "rrt_devices"
                selected_devices = st.multiselect("RRT — Geräte auswählen (Mehrfach)", options=devices, key=key_devices)

                # shared parameter filter for all selected devices
                # collect all parameters present in the dataset (or limit to selected devices)
                if selected_devices:
                    ser_params = pd.Series([], dtype=object)
                    if 'Parameter' in crrt_df.columns:
                        ser_params = _coerce_series(crrt_df['Parameter'])
                    all_opts = sorted(ser_params.dropna().unique().tolist())
                else:
                    all_opts = []

                keyp = "rrt_params"
                _render_checkbox_grid(st, all_opts, keyp, ncols=2)
                st.checkbox("Tägliche Mittelwerte — RRT (für alle Geräte)", value=st.session_state.get("rrt_avg", False), key="rrt_avg")
            else:
                st.info("Keine Geräte/Sub-Kategorien für RRT gefunden")
