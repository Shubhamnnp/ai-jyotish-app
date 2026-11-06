"""
Streamlit Cloud Entry Point for JyotishOS / BRAMHAHORA.
Executes src/jyotish/ui/app.py.
"""
import sys
from pathlib import Path

# Ensure project root is in sys.path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Execute main Streamlit app
target_app = root_dir / "src" / "jyotish" / "ui" / "app.py"
with open(target_app, encoding="utf-8") as f:
    code = compile(f.read(), str(target_app), "exec")
    exec(code, globals(), locals())
