import pandas as pd
import streamlit as st
from typing import Optional

# reuse checkbox-grid helper if available, otherwise define a small fallback
try:
    from ui.selection_panel import _render_checkbox_grid
except Exception:
    def _safe_key(base: str) -> str:
        return "".join([c if c.isalnum() else "_" for c in str(base)])

    def _render_checkbox_grid(container, options, list_key: str, ncols: int = 2):
        if not options:
            container.info("Keine Optionen vorhanden")
            st.session_state.setdefault(list_key, [])
            return []
        inited_key = f"{list_key}__inited"
        if not st.session_state.get(inited_key, False):
            st.session_state.setdefault(list_key, [])
            for opt in options:
                st.session_state[f"{list_key}__chk__{_safe_key(opt)}"] = False
            st.session_state[inited_key] = True
        cols = container.columns(ncols)
        for i, opt in enumerate(options):
            col = cols[i % ncols]
            chk_key = f"{list_key}__chk__{_safe_key(opt)}"
            default = True if (st.session_state.get(list_key) and opt in st.session_state.get(list_key)) else False
            with col:
                container.checkbox(str(opt), value=default, key=chk_key)
        selected = [opt for opt in options if st.session_state.get(f"{list_key}__chk__{_safe_key(opt)}", False)]
        st.session_state[list_key] = selected
        return selected


def render_therapy_view(df: Optional[pd.DataFrame], therapy_label: str, key_prefix: str, start_dt=None, end_dt=None):
    """
    Generic renderer for therapy-style views where multiple devices (Sub-Kategorie)
    exist and parameters apply per device (MCS, RRT).

    Shared selection model: one multiselect for parameters (applies to all devices)
    and one avg checkbox (applies to all devices). Devices are selected via
    a multiselect; for each selected device a filtered table/aggregation is shown.
    """
    st.header(f"{therapy_label}")

    if df is None or df.empty:
        st.info(f"Keine Daten für {therapy_label} vorhanden")
        return None

    # devices
    ser_devs = df['Sub-Kategorie'] if 'Sub-Kategorie' in df.columns else pd.Series([], dtype=object)
    if not isinstance(ser_devs, pd.Series):
        try:
            ser_devs = pd.Series(ser_devs)
        except Exception:
            ser_devs = pd.Series([], dtype=object)
    devices = sorted(ser_devs.dropna().unique().tolist())
    if not devices:
        st.info(f"Keine Geräte/Sub-Kategorien für {therapy_label} gefunden")
        return None

    key_devices = f"{key_prefix}_devices"
    # render device selection as checkbox grid for compactness and persistence
    selected_devices = _render_checkbox_grid(st, devices, key_devices, ncols=2)

    # shared params
    all_params_ser = df['Parameter'] if 'Parameter' in df.columns else pd.Series([], dtype=object)
    if not isinstance(all_params_ser, pd.Series):
        try:
            all_params_ser = pd.Series(all_params_ser)
        except Exception:
            all_params_ser = pd.Series([], dtype=object)
    all_opts = sorted(all_params_ser.dropna().unique().tolist())

    shared_params_key = f"{key_prefix}_params"
    # default to unchecked
    st.session_state.setdefault(shared_params_key, [])
    st.session_state.setdefault(f"{key_prefix}_avg", False)
    with st.expander(f"Parameter — {therapy_label}", expanded=False):
        # present shared params as checkbox grid to save space
        shared_params_selected = _render_checkbox_grid(st, all_opts, shared_params_key, ncols=3)
        shared_avg_key = f"{key_prefix}_avg"
    avg_shared = st.checkbox("Tägliche Mittelwerte (für alle Geräte)", value=st.session_state.get(shared_avg_key, False), key=shared_avg_key)

    # Combine selected devices into a single dataframe and render once
    if not selected_devices:
        st.info("Keine Geräte ausgewählt — bitte wähle mindestens ein Gerät aus.")
        return None

    combined = df[df['Sub-Kategorie'].isin(selected_devices)].copy()

    # filter by shared parameters if provided
    if shared_params_selected:
        combined = combined[combined['Parameter'].isin(shared_params_selected)]

    # normalize timestamp column
    if 'timestamp_parsed' not in combined.columns and 'Zeit' in combined.columns:
        try:
            combined['timestamp_parsed'] = pd.to_datetime(combined['Zeit'], errors='coerce')
        except Exception:
            combined['timestamp_parsed'] = pd.to_datetime(combined['Zeit'], errors='coerce')

    if start_dt is not None and end_dt is not None and 'timestamp_parsed' in combined.columns:
        combined = combined[(combined['timestamp_parsed'] >= start_dt) & (combined['timestamp_parsed'] <= end_dt)]

    # if avg is requested, aggregate per date, parameter and device
    if st.session_state.get(shared_avg_key, False):
        if 'timestamp_parsed' not in combined.columns:
            st.warning("Keine Zeitstempel zum Aggregieren vorhanden")
            st.write(combined)
            return combined
        agg = combined.copy()
        agg['date'] = agg['timestamp_parsed'].dt.date
        candidate_cols = ['Wert', 'value', 'Value', 'value_numeric']
        col_to_use = None
        for c in candidate_cols:
            if c in agg.columns:
                col_to_use = c
                break
        if col_to_use is not None:
            agg['value_numeric'] = pd.to_numeric(agg[col_to_use], errors='coerce')
        else:
            agg['value_numeric'] = pd.Series([pd.NA] * len(agg), index=agg.index, dtype='float')
        # perform grouped aggregation: numeric mean when numbers available,
        # otherwise pick a median string (or the single string if only one present)
        groups = agg.groupby(['date', 'Parameter', 'Sub-Kategorie'], dropna=False)
        rows = []
        for (date, param, dev), g in groups:
            cnt_total = len(g)
            # attempt numeric conversion on the chosen source column
            if col_to_use is not None and col_to_use in g.columns:
                num = pd.to_numeric(g[col_to_use], errors='coerce')
            else:
                num = pd.Series([pd.NA] * len(g), index=g.index)
            cnt_numeric = int(num.notna().sum())
            if cnt_numeric > 0:
                value_mean = float(num.mean())
            else:
                # fallback: pick median string from non-null original values
                if col_to_use is not None and col_to_use in g.columns:
                    vals = g[col_to_use].dropna().astype(str).tolist()
                else:
                    vals = []
                if not vals:
                    value_mean = pd.NA
                else:
                    vals_sorted = sorted(vals)
                    mid = len(vals_sorted) // 2
                    value_mean = vals_sorted[mid]
            rows.append({
                'date': date,
                'Parameter': param,
                'Sub-Kategorie': dev,
                'value_mean': value_mean,
                'count_numeric': cnt_numeric,
                'count_total': cnt_total,
            })

        grouped = pd.DataFrame(rows)
        # rename and reorder columns for readability: Datum - Gerät - Parameter - Wert - Count
        grouped = grouped.rename(columns={'Sub-Kategorie': 'Gerät', 'value_mean': 'Wert', 'count_total': 'Count'})
        cols_wanted = [c for c in ['date', 'Gerät', 'Parameter', 'Wert', 'Count'] if c in grouped.columns]
        grouped = grouped[cols_wanted].copy()
        # format/round numeric Wert entries where possible
        if 'Wert' in grouped.columns:
            try:
                # only round numeric entries, leave strings untouched
                grouped['Wert'] = grouped['Wert'].apply(lambda v: round(v, 3) if isinstance(v, (int, float)) and not pd.isna(v) else v)
            except Exception:
                pass
        if 'date' in grouped.columns:
            grouped = grouped.rename(columns={'date': 'Datum'})

        st.write(grouped)
        return grouped

    # otherwise show combined table with a device column
    display_cols = []
    # prefer human-friendly columns
    for c in ['Sub-Kategorie', 'Zeit', 'Parameter', 'Wert', 'value', 'unit']:
        if c in combined.columns:
            display_cols.append(c)
    if display_cols:
        display_df = combined[display_cols].copy()
        if 'Sub-Kategorie' in display_df.columns:
            display_df = display_df.rename(columns={'Sub-Kategorie': 'Gerät'})
        if 'Wert' in display_df.columns:
            try:
                display_df['Wert'] = display_df['Wert'].astype(str).fillna("")
            except Exception:
                display_df['Wert'] = display_df['Wert'].apply(lambda x: "" if pd.isna(x) else str(x))
        st.write(display_df)
        return display_df
    else:
        st.write(combined)
        return combined
