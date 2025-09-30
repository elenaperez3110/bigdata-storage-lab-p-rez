# --- Añadir raíz del repo al PYTHONPATH para poder importar 'src' desde /app ---
import os, sys
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # carpeta raíz del repo
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
# ------------------------------------------------------------------------------

