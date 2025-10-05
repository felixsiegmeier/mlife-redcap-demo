import sys
from pathlib import Path

# Kleine Launcher-Datei, die Streamlit so startet, dass PyInstaller ein einzelnes EXE erzeugen kann.
# Wir setzen argv so, als würden wir `streamlit run app.py` ausführen.

if __name__ == "__main__":
    import platform
    script = "app.py"
    exe_dir = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent
    try:
        os_cwd = str(exe_dir)
        import os
        os.chdir(os_cwd)
    except Exception:
        pass
    # Setze die Serveradresse auf 127.0.0.1, um die lokale Begrenzung zu aktivieren
    sys.argv = ["streamlit", "run", script, "--server.headless=true", "--server.address=127.0.0.1"]
    try:
        from streamlit.web import cli as stcli
        sys.exit(stcli.main())
    except Exception as e:
        print("Fehler beim Starten von Streamlit:", e)
        raise
