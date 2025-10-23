# Clean M-Life

Eine Streamlit-Anwendung zur Verarbeitung und Visualisierung medizinischer Patientendaten.

## Programmablauf und Datenfluss

Das Projekt folgt einem strukturierten Ablauf von der Dateneingabe bis zur Anzeige. Nachfolgend eine schematische Übersicht des Datenflusses:

```
[1. Datenquelle (Input)]
    ↓
[2. Parsing & Transformation]
    ↓
[3. Speicherung (State)]
    ↓
[4. Aggregation (optional)]
    ↓
[5. Anzeige (Views)]
```

### Detaillierte Schritte:

#### 1. **Datenquelle (Input)**
- **Wo:** `data/` Ordner (z.B. `gesamte_akte.csv`, `vitalvalues_overview.csv` usw.)
- **Was:** CSV-Dateien mit medizinischen Daten (Vitals, Lab, ECMO, Medikation, etc.)
- **Wie:** Benutzer lädt Datei über Startpage (`views/startpage.py`) hoch.
- **Fluss:** Datei wird an `StateProvider.parse_data_to_state()` übergeben.

#### 2. **Parsing & Transformation**
- **Wo:** `services/data_parser.py` (DataParser-Klasse)
- **Was:** Rohdaten aus CSV werden in strukturierte DataFrames umgewandelt.
- **Spezifische Parser:**
  - `parse_vitals_data()` → Vitals (Herzfrequenz, Blutdruck, etc.)
  - `parse_lab_data()` → Lab-Werte (Blutgase, Elektrolyte, etc.)
  - `parse_ecmo_data()` → ECMO-Daten
  - `parse_medication_data()` → Medikamentengaben
  - `parse_respiratory_data()` → Respiratorwerte
  - `parse_crrt_data()` → CRRT-Daten
  - `parse_impella_data()` → Impella-Daten
  - `parse_fluidbalance_data()` → Flüssigkeitsbilanz
- **Transformation:** Daten werden in Pydantic-Modelle (`schemas/parse_schemas/`) validiert und in DataFrames konvertiert.
- **Hilfsfunktionen:** `_clean_csv()`, `_split_blocks()` (teilt CSV in Blöcke nach Headern).
- **Fluss:** DataParser gibt DataFrames zurück, die in `AppState.parsed_data` gespeichert werden.

#### 3. **Speicherung (State)**
- **Wo:** `state_provider/state_provider_class.py` (StateProvider-Klasse)
- **Was:** Geparsed DataFrames werden im Streamlit-Session-State (`st.session_state`) gespeichert.
- **Struktur:** `AppState` (aus `schemas/app_state_schemas/app_state.py`) enthält:
  - `parsed_data`: Dict mit DataFrames (z.B. `lab`, `vitals`, `ecmo`)
  - UI-State: Ausgewählte Views, Filter, Zeitbereiche
  - Metadaten: Dateiname, Zeitbereich
- **Fluss:** Nach Parsing wird State aktualisiert; Views greifen darauf zu.

#### 4. **Aggregation (optional, für spezifische Ansichten)**
- **Wo:** `services/value_aggregation/` (z.B. `lab_aggregator.py`, `vitals_aggregator.py`)
- **Was:** Rohdaten werden aggregiert (Median, Mittelwert, Min/Max) für bestimmte Parameter und Zeiträume.
- **Beispiele:**
  - `get_lab_value(date, category, parameter, selection="median")` → Aggregiert Lab-Werte pro Tag.
  - Ähnlich für Vitals.
- **Fluss:** Aggregatoren holen Daten aus State, berechnen Werte und geben sie zurück (z.B. für Formulare oder Charts).

#### 5. **Anzeige (Views)**
- **Wo:** `views/` Ordner (z.B. `lab_data.py`, `vitals_data.py`, `homepage.py`)
- **Was:** Daten aus State werden in Streamlit-UI angezeigt (Tabellen, Charts, Formulare).
- **Spezifische Views:**
  - `render_lab_data()`: Filtert und visualisiert Lab-Daten (mit Altair-Charts).
  - `render_vitals_data()`: Zeigt Vitals (z.B. Herzfrequenz-Kurven).
  - `lab_form()`: Formular für aggregierte Lab-Einträge (verwendet Aggregatoren).
  - `render_homepage()`: Übersicht mit Patientendaten.
  - `render_sidebar()`: Navigation und Filter (Zeitbereich, Kategorien).
- **Fluss:** Views holen gefilterte Daten aus State, rendern UI; Änderungen (z.B. Filter) aktualisieren State.

### Zusätzliche Hinweise:
- **State-Management:** Alles läuft über `StateProvider` – zentraler Punkt für Änderungen.
- **Änderungen machen:** 
  - Neue Parser: In `DataParser` hinzufügen und in `parse_data_to_state()` aufrufen.
  - Neue Aggregation: Neue Funktion in `value_aggregation/` erstellen.
  - Neue Views: Neue Datei in `views/` und in `app.py` registrieren.
  - Schemas: In `schemas/` anpassen für neue Datenmodelle.
- **Abhängigkeiten:** Verwendet Pandas für DataFrames, Pydantic für Validierung, Altair für Charts.

## Installation

1. Klone das Repository.
2. Installiere Abhängigkeiten: `pip install -r requirements.txt`
3. Starte die App: `streamlit run app.py`

## Verwendung

Lade eine CSV-Datei hoch und navigiere durch die verschiedenen Ansichten zur Datenanalyse.
