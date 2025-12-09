#!/usr/bin/env python3
"""
Grundlegender Test für die Swagger API
"""

import requests
import time
import subprocess
import signal
import os
from threading import Thread

def test_swagger_endpoints():
    """Testet die wichtigsten Swagger-Endpunkte"""
    base_url = "http://localhost:5000"
    
    # Warten bis Server bereit ist
    max_retries = 10
    for i in range(max_retries):
        try:
            response = requests.get(f"{base_url}/api/status", timeout=5)
            if response.status_code == 200:
                print("✅ Server ist bereit!")
                break
        except requests.exceptions.RequestException:
            if i == max_retries - 1:
                print("❌ Server konnte nicht erreicht werden")
                return False
            print(f"⏳ Warte auf Server... ({i+1}/{max_retries})")
            time.sleep(1)
    
    # Test Swagger UI
    try:
        response = requests.get(f"{base_url}/swagger/", timeout=5)
        print(f"📊 Swagger UI: {response.status_code} ({'✅' if response.status_code == 200 else '❌'})")
    except Exception as e:
        print(f"❌ Swagger UI Fehler: {e}")
    
    # Test API Status
    try:
        response = requests.get(f"{base_url}/api/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"🔧 API Status: ✅ {data.get('message', 'OK')}")
        else:
            print(f"❌ API Status Fehler: {response.status_code}")
    except Exception as e:
        print(f"❌ API Status Fehler: {e}")
    
    # Test Lieferanten Endpoint
    try:
        response = requests.get(f"{base_url}/api/lieferanten", timeout=5)
        print(f"🏢 Lieferanten API: {response.status_code} ({'✅' if response.status_code == 200 else '❌'})")
        if response.status_code == 200:
            data = response.json()
            print(f"   📦 Anzahl Lieferanten: {len(data)}")
    except Exception as e:
        print(f"❌ Lieferanten API Fehler: {e}")
    
    return True

if __name__ == "__main__":
    print("🧪 Teste Swagger API Endpoints")
    print("=" * 40)
    
    # Starte Server im Hintergrund
    print("🚀 Starte API Server...")
    import sys
    sys.path.append('.')
    
    # Import und Test direkt
    try:
        from app_swagger import app
        
        # Teste in einem separaten Thread
        def run_server():
            app.run(debug=False, host='127.0.0.1', port=5000, use_reloader=False)
        
        server_thread = Thread(target=run_server, daemon=True)
        server_thread.start()
        
        time.sleep(3)  # Warten bis Server läuft
        
        # Tests ausführen
        test_swagger_endpoints()
        
        print("\n✅ Swagger API Tests abgeschlossen!")
        print("🌐 Öffne http://localhost:5000/swagger/ im Browser")
        
    except Exception as e:
        print(f"❌ Fehler beim Testen: {e}")
    
    print("\n💡 Verwende 'python start_swagger.py' zum Starten der API")