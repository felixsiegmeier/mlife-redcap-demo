import streamlit as st
import pandas as pd
from typing import List, Optional
try:
    from ui.selection_panel import _render_checkbox_grid
except Exception:
    def _render_checkbox_grid(container, options, list_key: str, ncols: int = 2, format_func=None):
        # minimal fallback: render simple multiselect
        container.write("(Parameter-Auswahl-Fallback)")
        val = container.multiselect("Parameter", options=options, key=list_key)
        st.session_state[list_key] = val
        return val


def render_overview(dfs: Optional[dict] = None, key_prefixes: Optional[List[str]] = None, start_dt=None, end_dt=None) -> None:
    """
    Zeige ein Formular, in dem der Nutzer einen Patienten-Key eingibt und
    alle in den einzelnen Views ausgewählten Parameter als editierbare
    Felder prüft/ergänzt, bevor ein (Demo-)Senden an eine API erfolgt.

    Verhalten:
    - Sammelt alle session_state Keys, die auf '_params' enden.
    - Respektiert das zugehörige '<prefix>_avg' Flag: falls gesetzt, wird
      das Feld als "Mittelwert" gekennzeichnet (es erscheint nur ein Feld
      pro Parameter zur Eingabe des Mittelwerts).
    - Nutzt ein Streamlit-Formular, validiert den Patienten-Key und sammelt
      die eingegebenen Werte in `st.session_state['overview_payload']` als
      Demo-Payload (keine echte API-Aufruf-Implementierung).
    """
    st.header("Übersicht — editierbare Kopien der Ansichten")

    # Erwarte ein dict von DataFrames (prefix -> DataFrame)
    dfs = dfs or {}
    if not key_prefixes:
        key_prefixes = sorted(dfs.keys())
    if not key_prefixes:
        st.info("Keine DataFrames übergeben — keine Übersicht möglich.")
        return

    # (Nicht mehr anzeigen: statische Auflistung der Selektionen entfällt —
    # stattdessen wird direkt die editierbare Tabelle angeboten.)

    # Erzeuge für jeden Eintrag ein eindeutiges Feld-Key für session_state
    def _safe_key(view, param):
        key = f"overview_field__{view}__{param}"
        return "".join(c if c.isalnum() or c in ('_', '-') else '_' for c in key)

    # Voreinstellungen für patient key
    patient_key = st.text_input("Patienten-Key", value=st.session_state.get('overview_patient_key', ''), help="Eindeutiger Schlüssel für den Patienten (wird an die API gesendet)")

    # Für jede View (prefix) erzeugen wir eine editierbare Kopie der aktuell
    # gefilterten/aggregierten Tabelle, wie sie die jeweiligen Views anzeigen.
    data_editor = getattr(st, 'data_editor', None) or getattr(st, 'experimental_data_editor', None)
    any_shown = False
    # friendly names for known prefixes (fallback to prefix itself)
    view_names = {
        'df1_vitals': 'Vitals',
        'df2_resp': 'Respirator',
        'df3_lab': 'Labor',
        'mcs_ecmo': 'MCS - ECMO',
        'mcs_impella': 'MCS - Impella',
        'rrt': 'RRT',
    }
    for prefix in key_prefixes:
        df = dfs.get(prefix)
        view_title = view_names.get(prefix, prefix)
        if df is None or (isinstance(df, pd.DataFrame) and df.empty):
            st.info(f"Keine Daten für {view_title} vorhanden")
            continue
        any_shown = True
        st.subheader(view_title)
        # Ensure there are parameter selections; if not (fresh session on deploy), offer selection here
        params_key = f"{prefix}_params"
        if params_key not in st.session_state or not st.session_state.get(params_key):
            # attempt to extract parameter options from df
            param_opts = []
            if df is not None:
                if 'Parameter' in df.columns:
                    param_opts = sorted(pd.Series(df['Parameter']).dropna().unique().tolist())
                elif 'parameter' in df.columns:
                    param_opts = sorted(pd.Series(df['parameter']).dropna().unique().tolist())
            if param_opts:
                with st.expander(f"Parameter-Auswahl für {view_title}", expanded=False):
                    _render_checkbox_grid(st, param_opts, params_key, ncols=3)

        # Entscheide ob therapy-like (hat 'Sub-Kategorie') oder numeric
        df_show = pd.DataFrame()
        if 'Sub-Kategorie' in df.columns:
            # therapy: filter by selected devices and shared params
            selected_devices = st.session_state.get(f"{prefix}_devices", [])
            if not selected_devices:
                st.info(f"Keine Geräte für {view_title} ausgewählt.")
                continue
            combined = df[df['Sub-Kategorie'].isin(selected_devices)].copy()
            shared_params = st.session_state.get(f"{prefix}_params", [])
            if shared_params:
                combined = combined[combined['Parameter'].isin(shared_params)]
            # normalize timestamp
            if 'timestamp_parsed' not in combined.columns and 'Zeit' in combined.columns:
                try:
                    combined['timestamp_parsed'] = pd.to_datetime(combined['Zeit'], errors='coerce')
                except Exception:
                    combined['timestamp_parsed'] = pd.to_datetime(combined['Zeit'], errors='coerce')
            if start_dt is not None and end_dt is not None and 'timestamp_parsed' in combined.columns:
                combined = combined[(combined['timestamp_parsed'] >= start_dt) & (combined['timestamp_parsed'] <= end_dt)]
            # if avg requested, aggregate per date/Parameter/Sub-Kategorie
            if st.session_state.get(f"{prefix}_avg", False):
                # similar aggregation as in views/therapy.py
                agg = combined.copy()
                if 'timestamp_parsed' in agg.columns:
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
                groups = agg.groupby(['date', 'Parameter', 'Sub-Kategorie'], dropna=False)
                rows = []
                for (date, param, dev), g in groups:
                    cnt_total = len(g)
                    if col_to_use is not None and col_to_use in g.columns:
                        num = pd.to_numeric(g[col_to_use], errors='coerce')
                    else:
                        num = pd.Series([pd.NA] * len(g), index=g.index)
                    cnt_numeric = int(num.notna().sum())
                    if cnt_numeric > 0:
                        value_mean = float(num.mean())
                    else:
                        vals = g[col_to_use].dropna().astype(str).tolist() if (col_to_use in g.columns) else []
                        if not vals:
                            value_mean = pd.NA
                        else:
                            vals_sorted = sorted(vals)
                            mid = len(vals_sorted) // 2
                            value_mean = vals_sorted[mid]
                    rows.append({'date': date, 'device': dev, 'parameter': param, 'value': value_mean})
                df_show = pd.DataFrame(rows)
            else:
                # build standardized table columns
                display_cols = []
                for c in ['Sub-Kategorie', 'Zeit', 'Parameter', 'Wert', 'value', 'unit']:
                    if c in combined.columns:
                        display_cols.append(c)
                if display_cols:
                    display_df = combined[display_cols].copy()
                    # rename for consistency
                    if 'Sub-Kategorie' in display_df.columns:
                        display_df = display_df.rename(columns={'Sub-Kategorie': 'device'})
                    if 'Wert' in display_df.columns:
                        try:
                            display_df['Wert'] = display_df['Wert'].astype(str).fillna("")
                        except Exception:
                            display_df['Wert'] = display_df['Wert'].apply(lambda x: "" if pd.isna(x) else str(x))
                    # standardize columns to 'date' if timestamp present
                    if 'Zeit' in display_df.columns:
                        try:
                            display_df['timestamp_parsed'] = pd.to_datetime(display_df['Zeit'], errors='coerce')
                            display_df['date'] = display_df['timestamp_parsed'].dt.date
                        except Exception:
                            pass
                    # choose a value column
                    if 'Wert' in display_df.columns:
                        display_df['value'] = display_df['Wert']
                    df_show = display_df.rename(columns={'Parameter': 'parameter'})
                else:
                    # nothing selected -> empty df
                    df_show = pd.DataFrame()
        else:
            # numeric-like view
            d = df.copy()
            # normalize parameter column name
            if 'parameter' not in d.columns and 'Parameter' in d.columns:
                d = d.rename(columns={'Parameter': 'parameter'})
            params_selected = st.session_state.get(f"{prefix}_params", [])
            if params_selected:
                d = d[d['parameter'].isin(params_selected)]
            if start_dt is not None and end_dt is not None and 'timestamp_parsed' in d.columns:
                d = d[(d['timestamp_parsed'] >= start_dt) & (d['timestamp_parsed'] <= end_dt)]
            if st.session_state.get(f"{prefix}_avg", False):
                if 'timestamp_parsed' not in d.columns:
                    st.warning(f"{view_title}: Keine Zeitstempel zum Aggregieren vorhanden")
                    df_show = d
                else:
                    agg = d.copy()
                    agg['date'] = agg['timestamp_parsed'].dt.date
                    candidate_cols = ['value', 'Wert', 'value_numeric']
                    col_to_use = None
                    for c in candidate_cols:
                        if c in agg.columns:
                            col_to_use = c
                            break
                    if col_to_use is not None:
                        val_series = pd.to_numeric(agg[col_to_use], errors='coerce')
                    else:
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
                    cols = ['date', 'parameter', 'value_mean', 'unit', 'count_numeric', 'count_total']
                    grouped = grouped[[c for c in cols if c in grouped.columns]]
                    # normalize to 'value'
                    if 'value_mean' in grouped.columns:
                        grouped = grouped.rename(columns={'value_mean': 'value'})
                    df_show = grouped
            else:
                display_cols = []
                for c in ['timestamp', 'parameter', 'value', 'Wert', 'unit']:
                    if c in d.columns:
                        display_cols.append(c)
                if display_cols:
                    display_df = d[display_cols].copy()
                    df_show = display_df.rename(columns={'Parameter': 'parameter'})
                else:
                    df_show = d.copy()

        # Build a uniform table for editing: columns -> date, device, parameter, value
        rows = []
        if df_show is None or (isinstance(df_show, pd.DataFrame) and df_show.empty):
            st.info(f"{prefix}: Keine Einträge nach Filterung.")
            continue
        for _, r in df_show.iterrows():
            # Normalize date: prefer 'date' or 'Datum' or any timestamp-like column
            raw_date = None
            if 'date' in r.index:
                raw_date = r.get('date')
            elif 'Datum' in r.index:
                raw_date = r.get('Datum')
            elif 'timestamp_parsed' in r.index:
                raw_date = r.get('timestamp_parsed')
            elif 'timestamp' in r.index:
                raw_date = r.get('timestamp')
            # convert to Python date if possible for consistent display
            date_val = None
            try:
                if raw_date is not None and not pd.isna(raw_date):
                    dt = pd.to_datetime(raw_date)
                    date_val = dt.date()
            except Exception:
                date_val = str(raw_date)

            parameter = r.get('parameter') if 'parameter' in r.index else (r.get('Parameter') if 'Parameter' in r.index else None)
            value = r.get('value') if 'value' in r.index else (r.get('Wert') if 'Wert' in r.index else None)
            # device column removed — we keep date, parameter, value
            rows.append({'date': date_val, 'parameter': parameter, 'value': value})

        edit_df = pd.DataFrame(rows)
        # show editable table
        try:
            edited = data_editor(edit_df, use_container_width=True) if data_editor is not None else edit_df
        except Exception:
            st.warning("Interaktive Tabellenbearbeitung nicht verfügbar; zeige statische Tabelle.")
            st.table(edit_df)
            edited = edit_df

        # sync edited values into session_state under unique keys and record metadata
        edits_for_prefix = []
        for _, row in edited.iterrows():
            view = prefix
            param = row.get('parameter')
            date = row.get('date')
            val = row.get('value')
            # create a stable key (prefix + parameter + date)
            parts = [str(view), str(param) if param is not None else 'no_param']
            if date is not None:
                parts.append(str(date))
            fld_key_base = '__'.join(parts)
            fld_key = _safe_key(fld_key_base, '')
            fld_key = f"overview_field__{fld_key}"
            st.session_state[fld_key] = "" if val is None else str(val)
            edits_for_prefix.append({'parameter': param, 'date': date, 'field_key': fld_key})
        # store edits metadata for payload construction
        ss_edits = st.session_state.setdefault('overview_edits', {})
        ss_edits[prefix] = edits_for_prefix
        st.session_state['overview_edits'] = ss_edits

    if not any_shown:
        st.info("Keine der angegebenen Views konnte dargestellt werden.")

    # Submit-Button unabhängig vom Modus
    if st.button("Validieren & (Demo-)Senden"):
        errors = []
        if not patient_key or str(patient_key).strip() == "":
            errors.append("Patienten-Key darf nicht leer sein.")
        # Build payload from recorded edits in st.session_state['overview_edits']
        payload = {'patient_key': patient_key, 'parameters': []}
        edits_store = st.session_state.get('overview_edits', {})
        for prefix, edits in edits_store.items():
            for e in edits:
                fld = e.get('field_key')
                val = st.session_state.get(fld, "")
                payload['parameters'].append({
                    'view': prefix,
                    'parameter': e.get('parameter'),
                    'date': e.get('date'),
                    'value': val,
                })

        if errors:
            for e in errors:
                st.error(e)
            st.warning("Bitte Fehler beheben und erneut absenden.")
        else:
            st.session_state['overview_patient_key'] = patient_key
            st.session_state['overview_payload'] = payload
            st.success("Payload validiert und (Demo) vorbereitet.")
            st.json(payload)
            st.info("Hinweis: Tatsächlicher API-Call ist noch nicht implementiert.")

