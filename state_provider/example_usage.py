"""
Beispiel für die Verwendung der StateProvider-Klasse
"""

from state_provider_class import StateProvider, state_provider

# Beispiel 1: Verwendung der Singleton-Instanz (empfohlen)
def example_with_singleton():
    """Beispiel mit der globalen state_provider Instanz"""
    
    # State abrufen
    current_state = state_provider.get_state()
    print(f"Current state: {current_state}")
    
    # Prüfen ob Daten vorhanden sind
    has_data = state_provider.has_parsed_data()
    print(f"Has parsed data: {has_data}")
    
    # Zeitbereich abrufen (falls vorhanden)
    time_range = state_provider.get_time_range()
    print(f"Time range: {time_range}")
    
    # State-Attribute aktualisieren
    state_provider.update_state(
        patient_id="12345",
        ward="ICU-1"
    )
    
    # Ausgewählten Zeitbereich setzen
    from datetime import date
    state_provider.set_selected_time_range(
        date(2024, 1, 1), 
        date(2024, 12, 31)
    )
    

# Beispiel 2: Eigene Instanz erstellen
def example_with_new_instance():
    """Beispiel mit einer neuen StateProvider Instanz"""
    
    # Neue Instanz erstellen
    my_state_provider = StateProvider()
    
    # Diese Instanz verwendet denselben Session State Key,
    # daher greift sie auf dieselben Daten zu wie die Singleton-Instanz
    current_state = my_state_provider.get_state()
    
    # Daten parsen (Beispiel - Datei muss existieren)
    # parsed_state = my_state_provider.parse_data_to_state("path/to/data.csv")
    

# Beispiel 3: Verwendung in Streamlit-Anwendung
def streamlit_example():
    """Beispiel für Streamlit-Integration"""
    import streamlit as st
    
    st.title("State Provider Beispiel")
    
    # State abrufen
    current_state = state_provider.get_state()
    
    # UI für Dateiupload
    uploaded_file = st.file_uploader("CSV-Datei hochladen", type="csv")
    
    if uploaded_file is not None:
        # Temporäre Datei speichern und parsen
        with open("temp_data.csv", "wb") as f:
            f.write(uploaded_file.getvalue())
        
        # Daten parsen und State aktualisieren
        try:
            parsed_state = state_provider.parse_data_to_state("temp_data.csv")
            st.success("Daten erfolgreich geparst!")
            
            # Zeitbereich anzeigen
            time_range = state_provider.get_time_range()
            if time_range:
                st.write(f"Zeitbereich: {time_range[0]} bis {time_range[1]}")
                
        except Exception as e:
            st.error(f"Fehler beim Parsen: {e}")
    
    # State-Informationen anzeigen
    if state_provider.has_parsed_data():
        st.write("✅ Daten sind verfügbar")
        
        # Zeitbereich-Auswahl
        time_range = state_provider.get_time_range()
        if time_range:
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Startdatum", value=time_range[0])
            with col2:
                end_date = st.date_input("Enddatum", value=time_range[1])
            
            # Ausgewählten Zeitbereich aktualisieren
            if st.button("Zeitbereich aktualisieren"):
                state_provider.set_selected_time_range(start_date, end_date)
                st.rerun()
    else:
        st.write("❌ Keine Daten verfügbar")
    
    # Reset-Button
    if st.button("State zurücksetzen"):
        state_provider.reset_state()
        st.rerun()


if __name__ == "__main__":
    print("StateProvider Beispiele")
    print("=" * 40)
    
    print("\n1. Singleton Beispiel:")
    example_with_singleton()
    
    print("\n2. Neue Instanz Beispiel:")
    example_with_new_instance()
    
    print("\n3. Für Streamlit-Beispiel führen Sie diese Datei in Streamlit aus:")
    print("   streamlit run example_usage.py")