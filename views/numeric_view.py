import pandas as pd
import streamlit as st
from typing import Optional
# Try to import the checkbox grid helper from the ui module; if not available,
# provide a small local fallback to avoid circular import issues during runtime.
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


def render_numeric_view(df: Optional[pd.DataFrame], label: str, key_prefix: str, start_dt=None, end_dt=None):
    """
    Generic renderer for numeric/parameter time-series views (Vitals, Respirator, Labor).

    Expects a DataFrame in the 'numerics' long format with columns roughly:
      - timestamp_parsed or timestamp
      - parameter
      - value
      - unit (optional)

    This function intentionally mirrors the behaviour of the previous
    specialized views (filter multiselect persisted in session_state, optional
    daily averaging) so migration is non-breaking.
    """
    st.header(f"{label}")
    filter_expander = st.expander(f"Filter — {label}", expanded=False)

    if df is None or df.empty:
        st.info(f"Keine Daten für {label} vorhanden")
        return None

    def _safe_write(df_to_show: pd.DataFrame):
        d = df_to_show.copy()
        for c in ('value', 'Wert'):
            if c in d.columns:
                try:
                    d[c] = d[c].astype(str).fillna("")
                except Exception:
                    d[c] = d[c].apply(lambda x: "" if pd.isna(x) else str(x))
        st.write(d)

    # normalize parameter column name
    if 'parameter' not in df.columns and 'Parameter' in df.columns:
        df = df.rename(columns={'Parameter': 'parameter'})

    params = []
    if 'parameter' in df.columns and not df['parameter'].isnull().all():
        params = sorted(df['parameter'].dropna().unique().tolist())

    params_key = f"{key_prefix}_params"
    # Always render parameter selection as a compact checkbox grid for numeric views
    with filter_expander:
        # ensure no implicit preselection: initialize stored selection to empty list
        st.session_state.setdefault(params_key, [])
        params_selected = _render_checkbox_grid(st, params, params_key, ncols=3)

    filtered = df.copy()
    if params_selected:
        filtered = filtered[filtered['parameter'].isin(params_selected)]
    else:
        st.sidebar.warning("Keine Parameter ausgewählt — Anzeige leer", icon="⚠️")

    if start_dt is not None and end_dt is not None and 'timestamp_parsed' in filtered.columns:
        filtered = filtered[(filtered['timestamp_parsed'] >= start_dt) & (filtered['timestamp_parsed'] <= end_dt)]

    avg_key = f"{key_prefix}_avg"
    # with filter_expander:
    avg_daily = st.checkbox("Tägliche Mittelwerte pro Parameter berechnen", value=st.session_state.get(avg_key, False), key=avg_key)

    if avg_daily:
        if 'timestamp_parsed' not in filtered.columns:
            st.warning("Keine Zeitstempel zum Aggregieren vorhanden")
            st.write(filtered)
            return filtered
        agg = filtered.copy()
        agg['date'] = agg['timestamp_parsed'].dt.date
        # select first available numeric-like column safely
        candidate_cols = ['value', 'Wert', 'value_numeric']
        col_to_use = None
        for c in candidate_cols:
            if c in agg.columns:
                col_to_use = c
                break
        if col_to_use is not None:
            val_series = pd.to_numeric(agg[col_to_use], errors='coerce')
        else:
            # fallback: empty numeric series with same index
            val_series = pd.Series([pd.NA] * len(agg), index=agg.index, dtype='float')
        agg['value_numeric'] = val_series
        grouped = (
            agg.groupby(['date', 'parameter', 'unit'], dropna=False)
            .agg(
            value_mean=('value_numeric', 'mean'),
            count_numeric=('value_numeric', lambda x: int(x.notna().sum())),
            count_total=('value_numeric', 'size'),
            )
            .reset_index()
        )
        # Sort columns: value_mean first, then unit
        cols = ['date', 'parameter', 'value_mean', 'unit', 'count_numeric', 'count_total']
        grouped = grouped[cols]
        _safe_write(grouped)
        return grouped

    # default table output
    # try to show common columns if present
    display_cols = []
    for c in ['timestamp', 'parameter', 'value', 'Wert', 'unit']:
        if c in filtered.columns:
            display_cols.append(c)
    if display_cols:
        display_df = filtered[display_cols].copy()
        _safe_write(display_df)
    else:
        display_df = filtered.copy()
        _safe_write(display_df)
    return filtered
