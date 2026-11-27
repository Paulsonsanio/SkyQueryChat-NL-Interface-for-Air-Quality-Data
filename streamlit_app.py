"""
Streamlit Community Cloud Entrypoint for SkyQueryChat.
This file allows Streamlit Community Cloud to auto-detect and deploy SkyQueryChat seamlessly.
"""
import runpy
from pathlib import Path

# Run app.py in the current global context
app_path = Path(__file__).resolve().parent / "app.py"
runpy.run_path(str(app_path), run_name="__main__")
