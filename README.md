# 🏢 Lagerverwaltung für Einrichtungshaus

Ein vollständiges Lagerverwaltungssystem für ein kleines Einrichtungshaus mit FIFO-Prinzip, Mindestmengen-Überwachung und REST-API.

## 🚀 Schnellstart

### Voraussetzungen
- Python 3.13+
- Git

### Installation & Setup
```bash
# Repository klonen
git clone <repository-url>
cd lagermgnt

# Virtual Environment aktivieren (bereits vorhanden)
cd backend
source bin/activate

# Abhängigkeiten installieren
pip install -r requirements.txt

# API starten mit Swagger UI
python start_swagger.py
```

### 📊 Swagger UI
Nach dem Start ist die interaktive API-Dokumentation verfügbar unter:
**http://localhost:5001/swagger/**

## 🏗️ Projekt-Struktur

```
lagermgnt/
├── CLAUDE.md                    # Vollständige Projektdokumentation
├── README.md                    # Diese Datei
├── backend/                     # Python Flask Backend
│   ├── app.py                   # Ursprüngliche Flask API
│   ├── app_swagger.py           # Swagger-dokumentierte API
│   ├── start_swagger.py         # API-Startscript
│   ├── models.py                # Datenmodell-Klassen
│   ├── database.py              # Datenbank-Schema und Verbindung
│   ├── inventory_manager.py     # Geschäftslogik (FIFO)
│   ├── reports.py               # Berichte und Analysen
│   ├── requirements.txt         # Python-Abhängigkeiten
│   ├── pytest.ini              # Test-Konfiguration
│   ├── tests/                   # 97 umfassende Tests
│   ├── datenmodell.png          # ER-Diagramm
│   └── SWAGGER_README.md        # Swagger-spezifische Dokumentation
└── main.py                      # Legacy-Haupteinstiegspunkt
```

## 💼 Geschäftslogik

### FIFO-Prinzip (First In, First Out)
- Automatischer Verkauf der ältesten Lagerbestände zuerst
- Exakte Kostenrechnung und Gewinnanalyse
- Transparente Nachvollziehbarkeit aller Transaktionen

### Mindestmengen-Überwachung
- Automatische Erkennung von Artikeln unter Mindestmenge
- Nachbestellempfehlungen mit Mengenberechnung
- Integration mit Lieferanten-Informationen

### Projekt-basierte Verkaufsverfolgung
- Alle Verkäufe sind spezifischen Projekten zugeordnet
- Kunde ↔ Projekt ↔ Verkauf Beziehungen
- Umfassende Projekt-Gewinnanalysen

## 🔧 API-Funktionalitäten

### Stammdaten-Management
- **Lieferanten:** Vollständiges CRUD
- **Artikel:** Mit Mindestmengen-Unterstützung
- **Kunden:** Management und Detailansichten
- **Projekte:** Projekt-spezifische Verkaufsverfolgung

### Lagerverwaltung
- **Wareneingänge:** FIFO-Einlagerung mit Preiserfassung
- **Lagerbestände:** Real-time Bestandsabfragen
- **Automatische Reduktion:** Bei Verkäufen nach FIFO

### Verkaufsabwicklung
- **FIFO-Verkäufe:** Automatische Zuordnung ältester Bestände
- **Projekt-Zuordnung:** Verkäufe immer projektbezogen
- **Preiserfassung:** Verkaufspreise für Gewinnrechnung

### Berichte & Analysen
- **Mindestmengen-Berichte:** Nachbestellempfehlungen
- **Lagerbestände:** Detailliert und zusammengefasst
- **Gewinn-Analysen:** Gesamt und projektspezifisch
- **Lagerumschlag:** Performance-Kennzahlen

## 🧪 Qualitätssicherung

### Test-Abdeckung: 97 Tests
- **71** ursprüngliche Tests
- **10** Mindestmengen-Tests
- **7** CRUD-Operations-Tests
- **9** Referenzielle-Integrität-Tests

```bash
# Alle Tests ausführen
pytest tests/ -v

# Spezifische Test-Gruppen
pytest tests/test_api_mindestmenge.py -v      # Mindestmengen-Features
pytest tests/test_crud_operations.py -v       # CRUD-Operationen  
pytest tests/test_referential_integrity.py -v # Datenintegrität
```

## 📊 Datenbank

### SQLite mit Foreign Key Constraints
- Lokale Datei: `lagerverwaltung.db`
- Automatische Schema-Migration
- Referenzielle Integrität auf DB-Level
- PRAGMA foreign_keys = ON

### Entitäten
- **Lieferanten** ↔ **Artikel** (1:N)
- **Kunden** ↔ **Projekte** (1:N)
- **Artikel** ↔ **Lagerbestand** (1:N)
- **Artikel** ↔ **Verkäufe** (1:N)
- **Projekte** ↔ **Verkäufe** (1:N)

## 🌐 API-Dokumentation

### Interaktive Swagger UI
- **Try-it-out:** Alle Endpoints direkt testbar
- **Vollständige Schemas:** Request/Response-Modelle
- **Beispieldaten:** Realistische API-Calls
- **OpenAPI 3.0:** Exportierbare Spezifikation

### Beispiel-API-Calls
```bash
# Lieferant anlegen
curl -X POST "http://localhost:5001/api/lieferanten" \
  -H "Content-Type: application/json" \
  -d '{"name": "Möbel Schmidt", "kontakt": "info@moebel-schmidt.de"}'

# Mindestmengen-Bericht
curl "http://localhost:5001/api/berichte/mindestmenge"
```

## 🔒 Datenschutz & Sicherheit

### Implementierte Sicherheitsfeatures
- **Input-Validierung:** Alle API-Eingaben validiert
- **SQL-Injection-Schutz:** Parametrisierte Queries
- **Referenzielle Integrität:** Schutz vor inkonsistenten Daten
- **Error-Handling:** Keine sensiblen Daten in Fehlermeldungen

### Empfehlungen für Produktion
- SSL/TLS-Verschlüsselung
- API-Authentifizierung
- Rate-Limiting
- Backup-Strategien

## 📈 Roadmap

### Mögliche Erweiterungen
- **Web-Frontend:** React/Vue.js GUI
- **Authentifizierung:** User-Management
- **Multi-Mandanten:** Mehrere Einrichtungshäuser
- **Barcode-Scanner:** Mobile Lager-Apps
- **Automatisierte Bestellungen:** Integration mit Lieferanten-APIs

## 🤝 Beiträge

Das Projekt wurde vollständig dokumentiert und getestet. Bei Fragen oder Erweiterungswünschen bitte Issues anlegen.

## 📜 Lizenz

Dieses Projekt steht unter einer proprietären Lizenz für das Einrichtungshaus.

---

**🌟 Ein vollständiges, produktionsreifes Lagerverwaltungssystem mit moderner API und umfassender Dokumentation!**