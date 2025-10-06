import pandas as pd
import streamlit as st
import os
import io
import json
import time
from services.clean_csv import cleanCSV
from services.split_blocks import splitBlocks
from services.parse_numerics import parseNumerics
from services.parse_from_all_patient_data import parse_from_all_patient_data
from views import render_vitals, render_respirator, render_lab, render_mcs, render_mcs_ecmo, render_mcs_impella, render_rrt
from ui.sidebar import render_sidebar_navigation
from logging_config import configure_logging

# Initialize logging
logger = configure_logging()

# Upload limits (in bytes). Default: 50 MB
_DEFAULT_MAX_MB = int(os.environ.get("ALLOW_UPLOAD_MAX_MB", 50))
UPLOAD_MAX_BYTES = _DEFAULT_MAX_MB * 1024 * 1024
# Control whether state dumps are allowed to be written to disk
ALLOW_STATE_DUMP = os.environ.get("ALLOW_STATE_DUMP", "0").strip() in ("1", "true", "True")


def run_app():
    st.set_page_config(page_title="clean-mlife Explorer", layout="wide")
    st.title("clean-mlife — Explorer für 'ALLE Patientendaten'")

    upload = st.file_uploader("CSV")
    # Support a smoke-test mode: if SMOKE_TEST=1, load a local CSV so the app doesn't wait for manual upload
    if upload is None and os.environ.get('SMOKE_TEST') == '1':
        sample_path = os.path.join(os.path.dirname(__file__), "data", "gesamte_akte.csv")
        # fallback: project relative path
        if not os.path.exists(sample_path):
            sample_path = os.path.join(os.getcwd(), "data", "gesamte_akte.csv")
        try:
            with open(sample_path, 'rb') as f:
                content = f.read()
            upload = io.BytesIO(content)
        except Exception as e:
            st.warning(f"SMOKE_TEST aktiv, aber Datei nicht gefunden oder nicht lesbar: {sample_path} — {e}")

    if upload is None:
        st.info("Bitte lade eine CSV-Datei hoch, um zu starten.")
        return
    # Read upload safely: enforce max size and robust decoding with fallbacks
    raw = upload.read()
    if hasattr(raw, '__len__') and len(raw) > UPLOAD_MAX_BYTES:
        st.error(f"Hochgeladene Datei ist zu groß (> {_DEFAULT_MAX_MB} MB). Bitte kleinere Datei wählen.")
        logger.warning("Upload blocked: file size exceeds limit")
        return

    # Try utf-8, then latin-1 fallback
    try:
        file = raw.decode('utf-8')
    except UnicodeDecodeError:
        try:
            file = raw.decode('latin-1')
            logger.info("Upload decoded with latin-1 as fallback")
        except Exception as e:
            st.error("Hochgeladene Datei kann nicht decodiert werden. Bitte prüfe das Encoding.")
            logger.exception("Failed to decode upload: %s", e)
            return
    DELIMITER = ";"

    clean_file = cleanCSV(file)
    split_blocks = splitBlocks(clean_file, DELIMITER)
    df_1 = parseNumerics(split_blocks.get("Vitaldaten", {}), DELIMITER)
    df_2 = parseNumerics(split_blocks.get("Respiratordaten", {}), DELIMITER)
    df_3 = parseNumerics(split_blocks.get("Labor", {}), DELIMITER)
    ecmo_df = parse_from_all_patient_data(split_blocks.get("ALLE Patientendaten", {}), "ecmo", DELIMITER)
    impella_df = parse_from_all_patient_data(split_blocks.get("ALLE Patientendaten", {}), "impella", DELIMITER)
    crrt_df = parse_from_all_patient_data(split_blocks.get("ALLE Patientendaten", {}), "hämofilter", DELIMITER)

    # Helper to safely extract parameter list from a dataframe for a given sub-category/device
    def _unique_params_for(dframe, dev):
        if dframe is None or dframe.empty:
            return []
        if 'Sub-Kategorie' not in dframe.columns or 'Parameter' not in dframe.columns:
            return []
        ser = dframe.loc[dframe['Sub-Kategorie'] == dev, 'Parameter']
        # ensure it's a pandas Series
        if not isinstance(ser, pd.Series):
            try:
                ser = pd.Series(ser)
            except Exception:
                return []
        return sorted(ser.dropna().unique().tolist())

    # Initialize session_state defaults for known widget keys before rendering widgets
    # For main parameter multiselects: default to all available params (if any)
    # Do not preselect parameter filters here; default to empty lists so
    # checkbox-grids render unchecked by default.
    st.session_state.setdefault("df1_vitals_params", [])
    st.session_state.setdefault("df1_vitals_avg", False)
    st.session_state.setdefault("df2_resp_params", [])
    st.session_state.setdefault("df2_resp_avg", False)
    st.session_state.setdefault("df3_lab_params", [])
    st.session_state.setdefault("df3_lab_avg", False)

    # NOTE: We intentionally avoid creating per-device session_state keys here.
    # Earlier iterations created keys like "mcs_ecmo_<device>_params" or
    # "rrt_tab_<device>_params" which produced legacy entries in
    # session_state and caused confusion. We now use shared per-therapy keys
    # (e.g. 'mcs_ecmo_params', 'mcs_impella_params', 'rrt_params') and let the
    # views render per-device tables while reading the shared selections.

    # Shared per-therapy parameter defaults (ECMO/Impella)
    # Shared per-therapy parameter defaults: leave empty so checkboxes are unchecked
    st.session_state.setdefault('mcs_ecmo_params', [])
    st.session_state.setdefault('mcs_ecmo_avg', False)
    st.session_state.setdefault('mcs_impella_params', [])
    st.session_state.setdefault('mcs_impella_avg', False)
    st.session_state.setdefault('rrt_params', [])
    st.session_state.setdefault('rrt_avg', False)

    # --- Automatic cleanup: remove legacy per-device session_state keys that
    # may have been created in earlier runs. We keep shared per-therapy keys
    # (e.g. 'mcs_ecmo_params', 'rrt_params'). This prevents old keys from
    # interfering with the shared selection widgets.
    removed_legacy = []
    def _devices_from(df):
        if df is None or df.empty or 'Sub-Kategorie' not in df.columns:
            return []
        ser = df['Sub-Kategorie']
        try:
            ser = pd.Series(ser)
        except Exception:
            return []
        return sorted(ser.dropna().unique().tolist())

    for dev in _devices_from(ecmo_df):
        k1 = f"mcs_ecmo_{dev}_params"
        k2 = f"mcs_ecmo_{dev}_avg"
        if k1 in st.session_state:
            st.session_state.pop(k1, None)
            removed_legacy.append(k1)
        if k2 in st.session_state:
            st.session_state.pop(k2, None)
            removed_legacy.append(k2)

    for dev in _devices_from(impella_df):
        k1 = f"mcs_impella_{dev}_params"
        k2 = f"mcs_impella_{dev}_avg"
        if k1 in st.session_state:
            st.session_state.pop(k1, None)
            removed_legacy.append(k1)
        if k2 in st.session_state:
            st.session_state.pop(k2, None)
            removed_legacy.append(k2)

    for dev in _devices_from(crrt_df):
        k1 = f"rrt_tab_{dev}_params"
        k2 = f"rrt_tab_{dev}_avg"
        if k1 in st.session_state:
            st.session_state.pop(k1, None)
            removed_legacy.append(k1)
        if k2 in st.session_state:
            st.session_state.pop(k2, None)
            removed_legacy.append(k2)

    if removed_legacy:
        logger.info("Removed legacy session_state keys: %s", removed_legacy)
        if ALLOW_STATE_DUMP:
            try:
                with open('removed_legacy_keys.log', 'a', encoding='utf-8') as f:
                    f.write(json.dumps({'removed': removed_legacy, 'ts': time.time()}, default=str) + '\n')
            except Exception:
                logger.exception("Failed to write removed_legacy_keys.log")

    # global date range + view navigation
    start_dt, end_dt, view_choice = render_sidebar_navigation([df_1, df_2, df_3])

    # NOTE: debug-only UI (persistence debug and state dump) removed to simplify sidebar.
    # If ad-hoc inspection of st.session_state is needed, use the 'Reset Auswahl (Checkboxen)'
    # button in the selection panel or inspect the saved session logs externally.

    # The interactive "Remove legacy per-device session_state keys" button was
    # removed: automatic cleanup already ran above and removes legacy keys on
    # startup; if you need an interactive removal, reintroduce a minimal UI
    # control here that calls the same removal logic.

    # Removed file-triggered debug sequence and smoke-simulation blocks that used
    # internal debug helpers. These were debug-only and referenced the removed
    # `_dump_state` helper; keeping them would leave undefined references.
    # If automated or file-triggered runs are desired, reintroduce a controlled
    # and explicit mechanism that does not mutate user session_state by default.

    # We no longer render a persistent selection panel. Each view shows its own
    # expandable filter section (in the main column). Keep a flag to indicate
    # persistent panel is not used so views render widgets themselves.
    st.session_state['use_persistent_selection_panel'] = False

    if view_choice == "Vitals":
        render_vitals(df_1, label="Vitaldaten", key_prefix="df1_vitals", start_dt=start_dt, end_dt=end_dt)
    elif view_choice == "Respirator":
        render_respirator(df_2, label="Respiratordaten", key_prefix="df2_resp", start_dt=start_dt, end_dt=end_dt)
    elif view_choice == "Labor":
        render_lab(df_3, label="Labor", key_prefix="df3_lab", start_dt=start_dt, end_dt=end_dt)
    elif view_choice == "MCS - ECMO":
        render_mcs_ecmo(ecmo_df, key_prefix="mcs_ecmo", start_dt=start_dt, end_dt=end_dt)
    elif view_choice == "MCS - Impella":
        render_mcs_impella(impella_df, key_prefix="mcs_impella", start_dt=start_dt, end_dt=end_dt)
    elif view_choice == "RRT":
        render_rrt(crrt_df, key_prefix="rrt_tab", start_dt=start_dt, end_dt=end_dt)
    elif view_choice == "Übersicht":
        from views.overview import render_overview
        # Pass the actual DataFrames so overview can build editable copies
        dfs = {
            'df1_vitals': df_1,
            'df2_resp': df_2,
            'df3_lab': df_3,
            'mcs_ecmo': ecmo_df,
            'mcs_impella': impella_df,
            'rrt_tab': crrt_df,
        }
        render_overview(dfs=dfs, key_prefixes=["df1_vitals", "df2_resp", "df3_lab", "mcs_ecmo", "mcs_impella", "rrt_tab"], start_dt=start_dt, end_dt=end_dt)
