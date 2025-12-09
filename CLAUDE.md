Ich möchte für ein kleines Einrichtungshaus, meine eingekauften Waren verwalten.
Es gibt verschiedene Lieferanten, die Einrichtungsgegenstände an mich liefern, die ich in Projekten wieder verkaufe.
Häufig muss ich mehr einkaufen als ich in den Projekten weiter verkaufen kann. Deshalb muss ich diese Gegenstände vernünftig verwalten können.
Die Lieferanten bieten mir netto Einkaufspreise pro Stück. Haben einen Artikelnummer und eine Artikelbezeichnung.

Meine Kunden verkaufe ich in den Projekten die Gegenstände zu einem höheren Preis weiter. 

Den Preis die der Kunde bezahlt brauche ich auch als Stückpreis netto.

Ich brauche eine Übersicht bei welchen Projekten ich welche Gegenstände verkauft habe und den übrig geblieben Mengen die ich im Lager habe.
Die Projekte haben eine eindeutige Projektbezeichnung.
Die Projekte haben eine Zuordnung zu einem Kunden.

## Backend-Technologie

**Framework:** Flask (Python)
- REST-API mit JSON-Responses
- CORS-Unterstützung für Frontend-Integration
- Umfassende Error-Behandlung
- Interactive Swagger UI Documentation

**Datenbank:** SQLite
- Lokale Datenbankdatei `lagerverwaltung.db`
- PRAGMA foreign_keys für Referenzielle Integrität
- Automatische Migrations-Unterstützung

**Testing:** pytest
- 97 Testfälle mit umfassender Abdeckung
- Isolierte Test-Datenbanken  
- Integration- und Unit-Tests
- CRUD-Operations und Referenzielle Integrität

**API-Documentation:** flask-restx (Swagger UI)
- Interactive API Documentation
- Try-it-out Funktionalität für alle Endpoints
- OpenAPI 3.0 Schema Export
- Vollständig typisierte Request/Response Models

**Architektur:**
- `app.py` - Flask-Anwendung und API-Routen
- `models.py` - Datenmodell-Klassen
- `database.py` - Datenbankverbindung und Schema
- `inventory_manager.py` - Geschäftslogik und FIFO-Implementierung
- `reports.py` - Berichts- und Analysefunktionen

**API-Endpoints:**
- `/api/lieferanten` - Lieferanten-Management (CRUD)
- `/api/artikel` - Artikel-Management mit Mindestmengen (CR)
- `/api/kunden` - Kunden-Management (CR + Detail)
- `/api/projekte` - Projekt-Management (CR + Detail)
- `/api/lager/eingang` - Wareneingänge (FIFO)
- `/api/lager/bestand` - Lagerbestandsabfragen
- `/api/verkauf` - Verkaufserfassung (FIFO)
- `/api/berichte/*` - Diverse Berichte und Analysen
- `/api/berichte/mindestmenge` - Mindestmengen-Überwachung

**Swagger UI:**
- **Interactive API Documentation:** http://localhost:5001/swagger/
- **Try-it-out Funktionalität:** Alle Endpoints direkt im Browser testbar
- **Vollständige Schemas:** Request/Response-Modelle dokumentiert
- **OpenAPI 3.0:** Exportierbare API-Spezifikation

## API-Nutzung

### Schnellstart
```bash
cd backend
source bin/activate
python start_swagger.py
```

Öffnet automatisch: **http://localhost:5001/swagger/**

### Beispiel-Workflow über API

1. **Lieferant anlegen**
```bash
curl -X POST "http://localhost:5001/api/lieferanten" \
  -H "Content-Type: application/json" \
  -d '{"name": "Möbel Schmidt", "kontakt": "info@moebel-schmidt.de"}'
```

2. **Artikel mit Mindestmenge anlegen**
```bash
curl -X POST "http://localhost:5001/api/artikel" \
  -H "Content-Type: application/json" \
  -d '{"artikelnummer": "ST-001", "bezeichnung": "Bürostuhl", "lieferant_id": 1, "mindestmenge": 5}'
```

3. **Kunden und Projekt anlegen**
```bash
# Kunde
curl -X POST "http://localhost:5001/api/kunden" \
  -H "Content-Type: application/json" \
  -d '{"name": "Büro AG", "kontakt": "einkauf@buero-ag.de"}'

# Projekt  
curl -X POST "http://localhost:5001/api/projekte" \
  -H "Content-Type: application/json" \
  -d '{"projektname": "Büroausstattung 2024", "kunde_id": 1}'
```

4. **Wareneingang buchen**
```bash
curl -X POST "http://localhost:5001/api/lager/eingang" \
  -H "Content-Type: application/json" \
  -d '{"artikelnummer": "ST-001", "menge": 10, "einkaufspreis": 89.50}'
```

5. **Verkauf buchen**
```bash
curl -X POST "http://localhost:5001/api/verkauf" \
  -H "Content-Type: application/json" \
  -d '{"projekt_id": 1, "artikelnummer": "ST-001", "verkaufte_menge": 3, "verkaufspreis": 149.99}'
```

6. **Mindestmengen-Bericht abrufen**
```bash
curl "http://localhost:5001/api/berichte/mindestmenge"
```

### Test-Abdeckung
**97 Tests** mit vollständiger CRUD- und Integritätsprüfung:
```bash
pytest tests/ -v
# 71 ursprüngliche Tests
# 10 Mindestmengen-Tests  
# 7 CRUD-Operations-Tests
# 9 Referenzielle-Integrität-Tests
```

## Datenmodell

### Hauptentitäten

**LIEFERANTEN**
- `id` INTEGER PRIMARY KEY
- `name` TEXT NOT NULL UNIQUE  
- `kontakt` TEXT

**ARTIKEL**
- `artikelnummer` TEXT PRIMARY KEY
- `bezeichnung` TEXT NOT NULL
- `lieferant_id` INTEGER FOREIGN KEY → lieferanten.id
- `mindestmenge` INTEGER DEFAULT 1

**KUNDEN** 
- `id` INTEGER PRIMARY KEY
- `name` TEXT NOT NULL
- `kontakt` TEXT

**PROJEKTE**
- `id` INTEGER PRIMARY KEY
- `projektname` TEXT NOT NULL UNIQUE
- `kunde_id` INTEGER FOREIGN KEY → kunden.id

### Transaktionsbereich

**LAGERBESTAND**
- `id` INTEGER PRIMARY KEY
- `artikelnummer` TEXT FOREIGN KEY → artikel.artikelnummer
- `verfuegbare_menge` INTEGER NOT NULL
- `einkaufspreis` REAL NOT NULL
- `einlagerungsdatum` TEXT NOT NULL

**VERKÄUFE**
- `id` INTEGER PRIMARY KEY  
- `projekt_id` INTEGER FOREIGN KEY → projekte.id
- `artikelnummer` TEXT FOREIGN KEY → artikel.artikelnummer
- `verkaufte_menge` INTEGER NOT NULL
- `verkaufspreis` REAL NOT NULL
- `verkaufsdatum` TEXT NOT NULL

### Beziehungen
- Lieferanten → Artikel (1:N)
- Kunden → Projekte (1:N) 
- Artikel → Lagerbestand (1:N)
- Artikel → Verkäufe (1:N)
- Projekte → Verkäufe (1:N)

### Geschäftslogik
- **FIFO-Prinzip**: Verkauf der ältesten Lagerbestände zuerst
- **Mindestmengen-Überwachung**: Automatische Erkennung von Artikeln unter Mindestmenge
- **Projektbezogene Nachverfolgung**: Alle Verkäufe sind Projekten zugeordnet
- **Gewinnanalyse**: Differenz zwischen Einkaufs- und Verkaufspreisen
- **Nachbestellempfehlungen**: Berechnung benötigter Mengen basierend auf Mindestbeständen

