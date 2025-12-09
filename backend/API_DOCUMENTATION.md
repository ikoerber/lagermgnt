# Lagerverwaltung API Dokumentation

## Übersicht

REST API für die Lagerverwaltung eines Einrichtungshauses.

**Base URL:** `http://localhost:5000/api`

## Installation und Start

```bash
cd backend
pip3 install -r requirements.txt
python3 app.py
```

## API Endpoints

### Status
- `GET /api/status` - API Status prüfen

### Lieferanten

- `GET /api/lieferanten` - Alle Lieferanten auflisten
- `POST /api/lieferanten` - Neuen Lieferanten anlegen
- `GET /api/lieferanten/{id}` - Spezifischen Lieferanten abrufen

**POST Body Beispiel:**
```json
{
  "name": "Möbel GmbH",
  "kontakt": "info@moebel-gmbh.de"
}
```

### Artikel

- `GET /api/artikel` - Alle Artikel auflisten
- `POST /api/artikel` - Neuen Artikel anlegen
- `GET /api/artikel/{artikelnummer}` - Spezifischen Artikel abrufen

**POST Body Beispiel:**
```json
{
  "artikelnummer": "STUHL-001",
  "bezeichnung": "Bürostuhl schwarz",
  "lieferant_id": 1
}
```

### Kunden

- `GET /api/kunden` - Alle Kunden auflisten
- `POST /api/kunden` - Neuen Kunden anlegen

**POST Body Beispiel:**
```json
{
  "name": "Firma ABC GmbH",
  "kontakt": "kontakt@firma-abc.de"
}
```

### Projekte

- `GET /api/projekte` - Alle Projekte auflisten
- `POST /api/projekte` - Neues Projekt anlegen
- `GET /api/projekte/{id}` - Projekt-Details mit Verkäufen

**POST Body Beispiel:**
```json
{
  "projektname": "Büroausstattung ABC",
  "kunde_id": 1
}
```

### Lager

- `POST /api/lager/eingang` - Lagereingang buchen
- `GET /api/lager/bestand` - Gesamten Lagerbestand abrufen
- `GET /api/lager/bestand/{artikelnummer}` - Lagerbestand für spezifischen Artikel

**POST Body Beispiel (Lagereingang):**
```json
{
  "artikelnummer": "STUHL-001",
  "menge": 10,
  "einkaufspreis": 49.99,
  "einlagerungsdatum": "2024-01-15"
}
```

### Verkauf

- `POST /api/verkauf` - Verkauf durchführen (FIFO-Prinzip)

**POST Body Beispiel:**
```json
{
  "projekt_id": 1,
  "artikelnummer": "STUHL-001",
  "verkaufte_menge": 3,
  "verkaufspreis": 79.99,
  "verkaufsdatum": "2024-01-20"
}
```

### Berichte

- `GET /api/berichte/lagerbestand?detailliert=true` - Lagerbestand-Bericht
- `GET /api/berichte/projekte` - Projekt-Übersicht
- `GET /api/berichte/gewinn?projekt_id={id}` - Gewinn-Analyse
- `GET /api/berichte/lagerumschlag` - Lagerumschlag-Analyse

## Beispiel-Workflow mit curl

### 1. Lieferanten anlegen
```bash
curl -X POST http://localhost:5000/api/lieferanten \
  -H "Content-Type: application/json" \
  -d '{"name": "Möbel GmbH", "kontakt": "info@moebel-gmbh.de"}'
```

### 2. Artikel anlegen
```bash
curl -X POST http://localhost:5000/api/artikel \
  -H "Content-Type: application/json" \
  -d '{"artikelnummer": "STUHL-001", "bezeichnung": "Bürostuhl schwarz", "lieferant_id": 1}'
```

### 3. Kunde anlegen
```bash
curl -X POST http://localhost:5000/api/kunden \
  -H "Content-Type: application/json" \
  -d '{"name": "Firma ABC", "kontakt": "kontakt@firma-abc.de"}'
```

### 4. Projekt anlegen
```bash
curl -X POST http://localhost:5000/api/projekte \
  -H "Content-Type: application/json" \
  -d '{"projektname": "Büroausstattung ABC", "kunde_id": 1}'
```

### 5. Ware einlagern
```bash
curl -X POST http://localhost:5000/api/lager/eingang \
  -H "Content-Type: application/json" \
  -d '{"artikelnummer": "STUHL-001", "menge": 10, "einkaufspreis": 49.99}'
```

### 6. Ware verkaufen
```bash
curl -X POST http://localhost:5000/api/verkauf \
  -H "Content-Type: application/json" \
  -d '{"projekt_id": 1, "artikelnummer": "STUHL-001", "verkaufte_menge": 3, "verkaufspreis": 79.99}'
```

### 7. Lagerbestand abfragen
```bash
curl http://localhost:5000/api/lager/bestand
```

### 8. Gewinn-Analyse
```bash
curl http://localhost:5000/api/berichte/gewinn
```

## HTTP Status Codes

- `200` - OK
- `201` - Created
- `400` - Bad Request (Validierungsfehler)
- `404` - Not Found
- `500` - Internal Server Error

## Fehler-Format

```json
{
  "error": "Beschreibung des Fehlers"
}
```

## Besonderheiten

- **FIFO-Verkauf**: Beim Verkauf werden automatisch die ältesten Lagerbestände zuerst verwendet
- **Mehrfach-Lagerbestände**: Derselbe Artikel kann mit verschiedenen Einkaufspreisen gelagert werden
- **Automatische Datumsfelder**: Wenn kein Datum angegeben wird, wird das aktuelle Datum verwendet