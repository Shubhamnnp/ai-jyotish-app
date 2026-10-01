"""
JyotishOS - Web Application Launcher
Runs FastAPI with Uvicorn and automatically opens the browser at http://localhost:8000/web/
"""

import sys
import time
import threading
import webbrowser
import uvicorn

def open_browser():
    time.sleep(1.2)
    webbrowser.open("http://localhost:8000/web/")

if __name__ == "__main__":
    print("=" * 70)
    print("🕉️  JyotishOS - Modern Vedic Astrology SaaS Web Application")
    print("🎨  Theme: Authentic Grahalakshanam (Royal Azure & Cyan)")
    print("🚀  Server: http://localhost:8000/web/")
    print("=" * 70)
    
    # Auto-open browser in background thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Run Uvicorn server
    uvicorn.run("src.jyotish.api.main:app", host="0.0.0.0", port=8000, reload=False)
