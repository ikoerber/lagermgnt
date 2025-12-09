#!/usr/bin/env python3
"""
Startscript für die Lagerverwaltung API mit Swagger UI
"""

import webbrowser
import time
import threading
from app_swagger import app

def open_swagger_ui():
    """Öffnet automatisch die Swagger UI im Browser"""
    time.sleep(2)  # Warten bis Server gestartet ist
    webbrowser.open('http://localhost:5001/swagger/')

if __name__ == '__main__':
    print("🚀 Starte Lagerverwaltung API mit Swagger UI...")
    print("")
    print("📊 Swagger UI: http://localhost:5001/swagger/")
    print("🔧 API Status: http://localhost:5001/api/status") 
    print("📖 Alle Endpoints: http://localhost:5001/")
    print("")
    print("💡 Drücke Ctrl+C zum Beenden")
    print("=" * 50)
    
    # Browser automatisch öffnen
    threading.Thread(target=open_swagger_ui, daemon=True).start()
    
    # Server starten
    app.run(debug=True, host='0.0.0.0', port=5001)