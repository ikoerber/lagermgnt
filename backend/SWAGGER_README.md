# 📊 Lagerverwaltung Swagger API

Eine vollständig dokumentierte REST-API für das Einrichtungshaus-Lagerverwaltungssystem mit interaktiver Swagger UI.

## 🚀 Schnellstart

### 1. Server starten
```bash
# Mit automatischem Browser-Start
python start_swagger.py

# Oder manuell
python app_swagger.py
```

### 2. Swagger UI öffnen
Öffne deinen Browser und gehe zu: **http://localhost:5000/swagger/**

### 3. API testen
Die Swagger UI ermöglicht es dir, alle Endpoints direkt im Browser zu testen!

## 📋 API-Übersicht

### 🏢 Lieferanten Management
- `GET /api/lieferanten` - Alle Lieferanten auflisten
- `POST /api/lieferanten` - Neuen Lieferanten anlegen
- `GET /api/lieferanten/{id}` - Lieferanten-Details abrufen
- `PUT /api/lieferanten/{id}` - Lieferanten aktualisieren
- `DELETE /api/lieferanten/{id}` - Lieferanten löschen (mit Integritätsprüfung)

### 📦 Artikel Management (mit Mindestmengen)
- `GET /api/artikel` - Alle Artikel auflisten (inkl. Mindestmengen)
- `POST /api/artikel` - Neuen Artikel anlegen (mit Mindestmenge)
- `GET /api/artikel/{artikelnummer}` - Artikel-Details abrufen

### 👥 Kunden Management
- `GET /api/kunden` - Alle Kunden auflisten
- `POST /api/kunden` - Neuen Kunden anlegen
- `GET /api/kunden/{id}` - Kunden-Details abrufen

### 🏗️ Projekt Management
- `GET /api/projekte` - Alle Projekte auflisten
- `POST /api/projekte` - Neues Projekt anlegen
- `GET /api/projekte/{id}` - Projekt-Details mit Verkäufen abrufen

### 📊 Lager Management (FIFO)
- `POST /api/lager/eingang` - Wareneingang buchen (FIFO-Einlagerung)
- `GET /api/lager/bestand` - Gesamten Lagerbestand abrufen
- `GET /api/lager/bestand/{artikelnummer}` - Artikel-spezifischen Bestand abrufen

### 💰 Verkauf Management (FIFO)
- `POST /api/verkauf` - Verkauf buchen (FIFO-Abgang)

### 📈 Berichte & Analysen
- `GET /api/berichte/mindestmenge` - **NEU:** Artikel unter Mindestmenge
- `GET /api/berichte/lagerbestand` - Lagerbestand-Berichte
- `GET /api/berichte/projekte` - Projekt-Übersichten
- `GET /api/berichte/gewinn` - Gewinn-Analysen
- `GET /api/berichte/lagerumschlag` - Lagerumschlag-Analysen

### 🔧 System
- `GET /api/status` - API-Status abrufen

## 💡 Besondere Features

### 🎯 Interaktive API-Dokumentation
- **Try it out!** - Teste alle Endpoints direkt in der Swagger UI
- **Vollständige Schemas** - Alle Request/Response-Modelle dokumentiert
- **Beispiele** - Realistische Beispieldaten für alle Endpoints
- **Fehlerbehandlung** - Dokumentierte Error-Codes und Meldungen

### 🔗 Referenzielle Integrität
- **Automatische Validierung** - Ungültige Referenzen werden abgelehnt
- **Schutz vor Löschungen** - Lieferanten mit Artikeln können nicht gelöscht werden
- **Konsistente Daten** - Foreign Key Constraints auf Datenbankebene

### 📊 FIFO-Geschäftslogik
- **Automatische FIFO-Abrechnung** - Älteste Bestände werden zuerst verkauft
- **Transparente Kostenrechnung** - Exakte Gewinn-/Verlustrechnung
- **Lagerbestand-Tracking** - Vollständige Nachvollziehbarkeit

### ⚠️ Mindestmengen-Überwachung
- **Automatische Erkennung** - Artikel unter Mindestmenge
- **Nachbestellempfehlungen** - Berechnete Nachbestellmengen
- **Lieferanten-Integration** - Direkte Zuordnung zu Lieferanten

## 🔍 API-Beispiele

### Lieferant anlegen
```bash
curl -X POST "http://localhost:5000/api/lieferanten" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Möbel-Zentrale GmbH",
    "kontakt": "bestellung@moebel-zentrale.de"
  }'
```

### Artikel mit Mindestmenge anlegen
```bash
curl -X POST "http://localhost:5000/api/artikel" \
  -H "Content-Type: application/json" \
  -d '{
    "artikelnummer": "ST-001",
    "bezeichnung": "Bürostuhl Premium",
    "lieferant_id": 1,
    "mindestmenge": 5
  }'
```

### Wareneingang buchen
```bash
curl -X POST "http://localhost:5000/api/lager/eingang" \
  -H "Content-Type: application/json" \
  -d '{
    "artikelnummer": "ST-001",
    "menge": 10,
    "einkaufspreis": 89.50
  }'
```

### Verkauf buchen
```bash
curl -X POST "http://localhost:5000/api/verkauf" \
  -H "Content-Type: application/json" \
  -d '{
    "projekt_id": 1,
    "artikelnummer": "ST-001", 
    "verkaufte_menge": 3,
    "verkaufspreis": 149.99
  }'
```

### Mindestmengen-Bericht abrufen
```bash
curl "http://localhost:5000/api/berichte/mindestmenge"
```

## 🛠️ Entwicklung

### Abhängigkeiten
```bash
pip install -r requirements.txt
```

### Tests ausführen
```bash
pytest tests/ -v
```

### API-Schema exportieren
Die vollständige OpenAPI 3.0 Spezifikation ist verfügbar unter:
**http://localhost:5000/swagger.json**

## 🎨 Swagger UI Features

- **📱 Responsive Design** - Funktioniert auf Desktop und Mobile
- **🔐 Authentifizierung** - Vorbereitet für zukünftige Auth-Implementierung  
- **📊 Schema-Validierung** - Automatische Request/Response-Validierung
- **💾 Request-Historie** - Swagger speichert deine letzten Requests
- **📋 Code-Generierung** - Export als curl, Python, JavaScript etc.

## 🚀 Produktive Nutzung

Für die produktive Nutzung empfehlen wir:
- **Gunicorn** statt dem Development-Server
- **Nginx** als Reverse Proxy
- **SSL/TLS** für HTTPS
- **Authentifizierung** für geschützte Endpoints
- **Rate Limiting** zur API-Absicherung

---

**🌟 Viel Spaß mit der vollständig dokumentierten Lagerverwaltung API!** 

Die interaktive Swagger UI macht es einfach, die API zu verstehen, zu testen und zu integrieren.