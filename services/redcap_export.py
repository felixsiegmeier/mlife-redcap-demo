from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time, datetime
from pathlib import Path
from typing import Any, Iterable, Optional, Type

import json
import pandas as pd
from pydantic import BaseModel

# Models we know about (imports are optional to avoid cycles)
try:
    from schemas.db_schemas.lab import LabModel as LabSegmentModel  # type: ignore
except Exception:  # pragma: no cover
    LabSegmentModel = None  # type: ignore

try:
    from schemas.db_schemas.vitals import VitalsModel as VitalsSegmentModel  # type: ignore
except Exception:  # pragma: no cover
    VitalsSegmentModel = None  # type: ignore

try:
    from schemas.db_schemas.respiratory import RespiratoryModel as RespiratorySegmentModel  # type: ignore
except Exception:  # pragma: no cover
    RespiratorySegmentModel = None  # type: ignore

try:
    from schemas.db_schemas.medication import MedicationModel as MedicationSegmentModel  # type: ignore
except Exception:  # pragma: no cover
    MedicationSegmentModel = None  # type: ignore


META_FIELDS = {
    "record_id",
    "redcap_event_name",
    "redcap_repeat_instrument",
    "redcap_repeat_instance",
}

# Instrument-Gruppierung: mehrere Segmente mappen auf ein REDCap-Instrument
INSTRUMENT_BY_MODEL: dict[str, str] = {
    # Vitals/Resp/Medication gehören in der REDCap-Struktur in das gemeinsame Formular
    # "Hemodynamics, Ventilation, Medication"
    "VitalsModel": "hemodynamics_ventilation_medication",
    "RespiratoryModel": "hemodynamics_ventilation_medication",
    "MedicationModel": "hemodynamics_ventilation_medication",
    # Labor ist eigenes Formular
    "LabModel": "labor",
}


@dataclass
class RedcapMeta:
    record_id: str
    redcap_event_name: str
    redcap_repeat_instrument: Optional[str] = None
    redcap_repeat_instance: Optional[int] = None

    def as_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "record_id": self.record_id,
            "redcap_event_name": self.redcap_event_name,
        }
        if self.redcap_repeat_instrument is not None:
            d["redcap_repeat_instrument"] = self.redcap_repeat_instrument
        if self.redcap_repeat_instance is not None:
            d["redcap_repeat_instance"] = self.redcap_repeat_instance
        return d


class Codebook:
    """
    Optionales Codebook zum Mapping von Label -> Code pro Feld.
    Format (JSON):
    {
      "vent_type": {"Invasive Ventilation": 1, "Non invasive Ventilation": 2, ...},
      "vent_spec": {"IPPV": 1, ...},
      ...
    }
    """

    def __init__(self, mapping: Optional[dict[str, dict[str, Any]]] = None) -> None:
        self.mapping: dict[str, dict[str, Any]] = mapping or {}

    @classmethod
    def from_file(cls, path: Path) -> "Codebook":
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return cls(mapping=data)
        return cls()

    def map_value(self, field: str, value: Any) -> Any:
        if value is None:
            return None
        # Bool als 0/1 ausgeben (REDCap-kompatibel)
        if isinstance(value, bool):
            return 1 if value else 0
        # Enums -> ihre Werte (string) extrahieren
        if hasattr(value, "value"):
            value = getattr(value, "value")
        # Datum/Zeit formatiert ausgeben
        if isinstance(value, date) and not isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")
        if isinstance(value, time):
            return value.strftime("%H:%M")
        if isinstance(value, datetime):
            return value.isoformat(sep=" ", timespec="seconds")
        # Checkboxfelder (name___n) sind bereits bool->0/1 abgedeckt
        # Falls ein Mapping für dieses Feld existiert, Label->Code abbilden
        fm = self.mapping.get(field)
        if isinstance(fm, dict):
            return fm.get(str(value), value)
        return value


def _model_fields_for_export(model: BaseModel) -> list[str]:
    # Nur die Felder dieses Segments (ohne Meta) exportieren
    return [k for k in model.model_fields.keys() if k not in META_FIELDS]


def _infer_instrument(model: BaseModel) -> str:
    name = model.__class__.__name__
    return INSTRUMENT_BY_MODEL.get(name, "unknown_instrument")


def segment_to_row(meta: RedcapMeta, segment: BaseModel, codebook: Optional[Codebook] = None) -> dict[str, Any]:
    """
    Baut eine einzelne Zeile für den REDCap-Import als Dict.
    Meta-Felder werden ergänzt, Segment-Felder nach alias exportiert, Werte formatiert/gemappt.
    """
    cb = codebook or Codebook()
    # Dump Segment als alias-Namen
    seg = segment.model_dump(by_alias=True, exclude_none=True)
    # Filter auf Segment-Felder
    allowed = set(_model_fields_for_export(segment))
    row: dict[str, Any] = {}
    # Meta + instrument
    row.update(meta.as_dict())
    instrument = _infer_instrument(segment)
    if instrument != "unknown_instrument":
        row.setdefault("redcap_repeat_instrument", instrument)
    # Werte mappen/formatieren
    for field, value in seg.items():
        if field in META_FIELDS:
            continue
        if field not in allowed:
            continue
        row[field] = cb.map_value(field, value)
    return row


def compose_rows(meta: RedcapMeta, segments: Iterable[BaseModel], codebook: Optional[Codebook] = None) -> list[dict[str, Any]]:
    """
    Gruppiert Segmente je Instrument/Instance und MERGT die Feldwerte in jeweils eine Zeile.
    So entsteht pro Instrument (und Instance) genau eine Import-Zeile.
    """
    cb = codebook or Codebook()
    grouped: dict[tuple[str, Optional[int]], dict[str, Any]] = {}

    for seg in segments:
        row = segment_to_row(meta, seg, cb)
        instrument = row.get("redcap_repeat_instrument", "unknown_instrument")
        instance = row.get("redcap_repeat_instance")
        key = (instrument, instance)
        base = grouped.setdefault(key, {**meta.as_dict(), "redcap_repeat_instrument": instrument})
        # Merge Feldwerte (spätere Segmente überschreiben ggf.)
        for k, v in row.items():
            if k in META_FIELDS:
                continue
            base[k] = v

    # Rückgabe als Liste von Zeilen
    return list(grouped.values())


def export_to_csv(meta: RedcapMeta, segments: Iterable[BaseModel], csv_path: Path, codebook_path: Optional[Path] = None) -> Path:
    """
    Baut aus Meta + Segment-Instanzen eine CSV, die in REDCap importierbar ist.
    - Bool -> 0/1
    - date/time/datetime werden formatiert
    - Enums per Codebook (falls vorhanden) in Codes gemappt
    - Segmente mit gleichem Instrument werden gemergt
    """
    codebook = Codebook.from_file(codebook_path) if codebook_path else Codebook()
    rows = compose_rows(meta, segments, codebook)

    # Spaltenreihenfolge: Meta zuerst, dann restliche Felder (stabil sortiert)
    if rows:
        cols_meta = [c for c in META_FIELDS if c in rows[0]]
        other_cols = sorted({k for r in rows for k in r.keys()} - set(cols_meta))
        cols = cols_meta + other_cols
        df = pd.DataFrame(rows, columns=cols)
    else:
        df = pd.DataFrame()

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, index=False)
    return csv_path


# -----------------------------
# Pandas-First Helper
# -----------------------------
def _alias_to_field_map(model_cls: Type[BaseModel]) -> dict[str, str]:
    """Build mapping from alias name -> internal field name for a Pydantic model."""
    m: dict[str, str] = {}
    for fname, f in model_cls.model_fields.items():  # type: ignore[attr-defined]
        alias = getattr(f, "alias", None) or fname
        m[str(alias)] = fname
    return m


def df_to_segments(
    meta: RedcapMeta,
    df: pd.DataFrame,
    model_cls: Type[BaseModel],
    column_map: Optional[dict[str, str]] = None,
    static_values: Optional[dict[str, Any]] = None,
) -> list[BaseModel]:
    """
    Wandelt einen DataFrame in Pydantic-Segmente um.

    Annahmen/Verhalten:
    - df-Spalten sind standardmäßig die REDCap-Feldnamen (Aliases der Pydantic-Modelle).
      Optional kann column_map verwendet werden: {df_col -> redcap_field_alias}.
    - Pflicht-Metafelder (record_id, redcap_event_name) werden aus meta ergänzt.
    - static_values kann genutzt werden, um für alle Zeilen konstante Werte zu setzen/überschreiben.
    - redcap_repeat_instance kann aus df kommen (falls Spalte existiert) oder über static_values.
    """
    alias_to_field = _alias_to_field_map(model_cls)
    segs: list[BaseModel] = []
    static_values = static_values or {}

    # Vorab die Spaltennamen im DF zu den Aliases normalisieren
    # Wenn eine column_map angegeben ist, wird df_col -> alias gemappt, sonst alias=col
    def row_to_kwargs(row: pd.Series) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            # Meta erforderlich, viele Modelle erwarten diese Felder
            "record_id": meta.record_id,
            "redcap_event_name": meta.redcap_event_name,
        }
        # redcap_repeat_instrument NICHT hier setzen; das wird im Export automatisch zugewiesen.

        for col, val in row.items():
            key_s = str(col)
            alias = column_map[key_s] if (column_map and key_s in column_map) else key_s
            field_name = alias_to_field.get(str(alias))
            if field_name is None:
                continue
            if field_name in META_FIELDS:
                # Erlaube Überschreiben von repeat_instance aus DF, falls vorhanden
                if field_name == "redcap_repeat_instance" and val is not None:
                    kwargs[field_name] = int(val) if pd.notna(val) else None
                continue
            kwargs[field_name] = val

        # Statische Werte zuletzt (dürfen row-Werte überschreiben)
        kwargs.update(static_values)
        return kwargs

    for _, row in df.iterrows():
        kwargs = row_to_kwargs(row)
        seg = model_cls(**kwargs)
        segs.append(seg)
    return segs


def export_from_dataframes(
    meta: RedcapMeta,
    frames: dict[Type[BaseModel], pd.DataFrame],
    out_csv: Path,
    column_maps: Optional[dict[Type[BaseModel], dict[str, str]]] = None,
    static_values: Optional[dict[Type[BaseModel], dict[str, Any]]] = None,
    codebook_path: Optional[Path] = None,
) -> Path:
    """
    High-Level: Nimmt mehrere DataFrames (je Segment-Modell) und schreibt eine gemergte REDCap-CSV.

    Parameter:
    - frames: {ModelClass -> DataFrame} mit Zeilen pro (record_id,event[,instance]).
      Die DataFrames sollten pro Zeile alle relevanten REDCap-Feld-Aliases des jeweiligen Modells enthalten.
    - column_maps: optional {ModelClass -> {df_col -> redcap_alias}} wenn DF-Spalten nicht bereits die Aliases sind.
    - static_values: optional {ModelClass -> {field_name -> value}} konstante Werte pro Segmentmodell.
    - codebook_path: optionaler Pfad zu einem JSON-Codebook für Label->Code Mapping.
    """
    column_maps = column_maps or {}
    static_values = static_values or {}

    all_segments: list[BaseModel] = []
    for model_cls, df in frames.items():
        cmap = column_maps.get(model_cls)
        svals = static_values.get(model_cls)
        segs = df_to_segments(meta, df, model_cls, column_map=cmap, static_values=svals)
        all_segments.extend(segs)

    return export_to_csv(meta, all_segments, out_csv, codebook_path=codebook_path)
