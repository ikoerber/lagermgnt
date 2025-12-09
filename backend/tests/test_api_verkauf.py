import pytest
from datetime import datetime

def test_verkauf_success(auth_client, sample_data):
    # Erst Lagereingang
    auth_client.post('/api/lager/eingang', json={
        'artikelnummer': sample_data['artikelnummer'],
        'menge': 10,
        'einkaufspreis': 49.99
    }, headers=auth_client.auth_headers)
    
    # Dann Verkauf
    verkauf_data = {
        'projekt_id': sample_data['projekt_id'],
        'artikelnummer': sample_data['artikelnummer'],
        'verkaufte_menge': 3,
        'verkaufspreis': 79.99,
        'verkaufsdatum': '2024-01-20'
    }
    
    response = auth_client.post('/api/verkauf', json=verkauf_data, headers=auth_client.auth_headers)
    assert response.status_code == 201
    
    response_data = response.get_json()
    assert response_data['message'] == 'Verkauf erfolgreich'
    assert response_data['projekt_id'] == verkauf_data['projekt_id']
    assert response_data['artikelnummer'] == verkauf_data['artikelnummer']
    assert response_data['verkaufte_menge'] == verkauf_data['verkaufte_menge']
    assert response_data['verkaufspreis'] == verkauf_data['verkaufspreis']

def test_verkauf_without_date(auth_client, sample_data):
    # Lagereingang
    auth_client.post('/api/lager/eingang', json={
        'artikelnummer': sample_data['artikelnummer'],
        'menge': 5,
        'einkaufspreis': 49.99
    }, headers=auth_client.auth_headers)
    
    # Verkauf ohne Datum
    verkauf_data = {
        'projekt_id': sample_data['projekt_id'],
        'artikelnummer': sample_data['artikelnummer'],
        'verkaufte_menge': 2,
        'verkaufspreis': 79.99
    }
    
    response = auth_client.post('/api/verkauf', json=verkauf_data, headers=auth_client.auth_headers)
    assert response.status_code == 201
    
    response_data = response.get_json()
    assert response_data['verkaufsdatum'] == datetime.now().strftime("%Y-%m-%d")

def test_verkauf_insufficient_stock(auth_client, sample_data):
    # Nur 5 Stück einlagern
    auth_client.post('/api/lager/eingang', json={
        'artikelnummer': sample_data['artikelnummer'],
        'menge': 5,
        'einkaufspreis': 49.99
    }, headers=auth_client.auth_headers)
    
    # Versuchen 10 Stück zu verkaufen
    verkauf_data = {
        'projekt_id': sample_data['projekt_id'],
        'artikelnummer': sample_data['artikelnummer'],
        'verkaufte_menge': 10,
        'verkaufspreis': 79.99
    }
    
    response = auth_client.post('/api/verkauf', json=verkauf_data, headers=auth_client.auth_headers)
    assert response.status_code == 500  # LagerError for insufficient stock
    assert 'nicht genügend' in response.get_json()['error'].lower()

def test_verkauf_missing_fields(auth_client):
    # Ohne Projekt-ID
    response = auth_client.post('/api/verkauf', json={
        'artikelnummer': 'TEST-001',
        'verkaufte_menge': 1,
        'verkaufspreis': 79.99
    }, headers=auth_client.auth_headers)
    assert response.status_code == 400
    assert 'error' in response.get_json()

def test_verkauf_fifo_principle(auth_client, sample_data):
    # Mehrere Lagereingänge zu verschiedenen Preisen und Zeiten
    eingaenge = [
        {'menge': 10, 'einkaufspreis': 45.00, 'einlagerungsdatum': '2024-01-10'},
        {'menge': 10, 'einkaufspreis': 50.00, 'einlagerungsdatum': '2024-01-15'},
        {'menge': 10, 'einkaufspreis': 55.00, 'einlagerungsdatum': '2024-01-20'}
    ]
    
    for eingang in eingaenge:
        auth_client.post('/api/lager/eingang', json={
            'artikelnummer': sample_data['artikelnummer'],
            **eingang
        }, headers=auth_client.auth_headers)
    
    # 15 Stück verkaufen (sollte 10 vom ersten + 5 vom zweiten Eingang nehmen)
    response = auth_client.post('/api/verkauf', json={
        'projekt_id': sample_data['projekt_id'],
        'artikelnummer': sample_data['artikelnummer'],
        'verkaufte_menge': 15,
        'verkaufspreis': 79.99
    }, headers=auth_client.auth_headers)
    assert response.status_code == 201
    
    # Verbleibenden Bestand prüfen (mit Zero-Einträgen)
    response = auth_client.get(f'/api/lager/bestand/{sample_data["artikelnummer"]}?include_zero=true', headers=auth_client.auth_headers)
    bestaende = response.get_json()
    
    # Erster Bestand sollte 0 sein
    # Zweiter Bestand sollte 5 sein (10 - 5)
    # Dritter Bestand sollte 10 sein (unverändert)
    verfuegbar = [b['verfuegbare_menge'] for b in sorted(bestaende, key=lambda x: x['einlagerungsdatum'])]
    assert verfuegbar == [0, 5, 10]

def test_verkauf_complete_stock_depletion(auth_client, sample_data):
    # Lagereingang
    auth_client.post('/api/lager/eingang', json={
        'artikelnummer': sample_data['artikelnummer'],
        'menge': 10,
        'einkaufspreis': 49.99
    }, headers=auth_client.auth_headers)
    
    # Kompletten Bestand verkaufen
    response = auth_client.post('/api/verkauf', json={
        'projekt_id': sample_data['projekt_id'],
        'artikelnummer': sample_data['artikelnummer'],
        'verkaufte_menge': 10,
        'verkaufspreis': 79.99
    }, headers=auth_client.auth_headers)
    assert response.status_code == 201
    
    # Bestand sollte leer sein
    response = auth_client.get('/api/lager/bestand', headers=auth_client.auth_headers)
    assert response.get_json() == []

def test_verkauf_invalid_projekt(auth_client, sample_data):
    # Lagereingang
    auth_client.post('/api/lager/eingang', json={
        'artikelnummer': sample_data['artikelnummer'],
        'menge': 5,
        'einkaufspreis': 49.99
    }, headers=auth_client.auth_headers)
    
    # Verkauf mit ungültiger Projekt-ID
    response = auth_client.post('/api/verkauf', json={
        'projekt_id': 999,
        'artikelnummer': sample_data['artikelnummer'],
        'verkaufte_menge': 1,
        'verkaufspreis': 79.99
    }, headers=auth_client.auth_headers)
    assert response.status_code == 404  # NotFoundError for invalid projekt

def test_multiple_verkaeufe_same_projekt(auth_client, sample_data):
    # Lagereingang
    auth_client.post('/api/lager/eingang', json={
        'artikelnummer': sample_data['artikelnummer'],
        'menge': 20,
        'einkaufspreis': 49.99
    }, headers=auth_client.auth_headers)
    
    # Mehrere Verkäufe
    verkaeufe = [
        {'verkaufte_menge': 3, 'verkaufspreis': 75.00},
        {'verkaufte_menge': 5, 'verkaufspreis': 80.00},
        {'verkaufte_menge': 2, 'verkaufspreis': 82.00}
    ]
    
    for verkauf in verkaeufe:
        response = auth_client.post('/api/verkauf', json={
            'projekt_id': sample_data['projekt_id'],
            'artikelnummer': sample_data['artikelnummer'],
            **verkauf
        }, headers=auth_client.auth_headers)
        assert response.status_code == 201
    
    # Projekt-Details prüfen
    response = auth_client.get(f'/api/projekte/{sample_data["projekt_id"]}', headers=auth_client.auth_headers)
    projekt_data = response.get_json()
    assert len(projekt_data['verkaeufe']) == 3
    
    # Berechnung: 3*75 + 5*80 + 2*82 = 225 + 400 + 164 = 789
    assert projekt_data['gesamtumsatz'] == 789.0