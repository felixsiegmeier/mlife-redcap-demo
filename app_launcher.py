import sys
from pathlib import Path

# Kleine Launcher-Datei, die Streamlit so startet, dass PyInstaller ein einzelnes EXE erzeugen kann.
# Wir setzen argv so, als würden wir `streamlit run app.py` ausführen.

if __name__ == "__main__":
    script = "app.py"

    # Falls das EXE an einem anderen Ort liegt, setzen wir das Arbeitsverzeichnis auf das Verzeichnis der EXE
    exe_dir = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent
    try:
        # Wechsel in das Projektverzeichnis (wichtig für relative Pfade zu data/ und services/)
        os_cwd = str(exe_dir)
        import os
        os.chdir(os_cwd)
    except Exception:
        pass

    sys.argv = ["streamlit", "run", script, "--server.headless=true"]
    try:
        # Streamlit's CLI entrypoint
        from streamlit.web import cli as stcli
        sys.exit(stcli.main())
    except Exception as e:
        print("Fehler beim Starten von Streamlit:", e)
        raise
