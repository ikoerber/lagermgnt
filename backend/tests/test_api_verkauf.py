import pytest
from auth_helper import client_with_auth
from datetime import datetime

def test_verkauf_success(client_with_auth):
    # Erst Lagereingang
    client_with_auth.auth.authenticated_post('/api/lager/eingang', json={
        'artikelnummer': 'TEST-001',
        'menge': 10,
        'einkaufspreis': 49.99
    })
    
    # Dann Verkauf
    verkauf_data = {
        'projekt_id': 1,
        'artikelnummer': 'TEST-001',
        'verkaufte_menge': 3,
        'verkaufspreis': 79.99,
        'verkaufsdatum': '2024-01-20'
    }
    
    response = client_with_auth.auth.authenticated_post('/api/verkauf', json=verkauf_data)
    assert response.status_code == 201
    
    response_data = response.get_json()
    assert response_data['message'] == 'Verkauf erfolgreich'
    assert response_data['projekt_id'] == verkauf_data['projekt_id']
    assert response_data['artikelnummer'] == verkauf_data['artikelnummer']
    assert response_data['verkaufte_menge'] == verkauf_data['verkaufte_menge']
    assert response_data['verkaufspreis'] == verkauf_data['verkaufspreis']

def test_verkauf_without_date(client_with_auth):
    # Lagereingang
    client_with_auth.auth.authenticated_post('/api/lager/eingang', json={
        'artikelnummer': 'TEST-001',
        'menge': 5,
        'einkaufspreis': 49.99
    })
    
    # Verkauf ohne Datum
    verkauf_data = {
        'projekt_id': 1,
        'artikelnummer': 'TEST-001',
        'verkaufte_menge': 2,
        'verkaufspreis': 79.99
    }
    
    response = client_with_auth.auth.authenticated_post('/api/verkauf', json=verkauf_data)
    assert response.status_code == 201
    
    response_data = response.get_json()
    assert response_data['verkaufsdatum'] == datetime.now().strftime("%Y-%m-%d")

def test_verkauf_insufficient_stock(client_with_auth):
    # Nur 5 Stück einlagern
    client_with_auth.auth.authenticated_post('/api/lager/eingang', json={
        'artikelnummer': 'TEST-001',
        'menge': 5,
        'einkaufspreis': 49.99
    })
    
    # Versuchen 10 Stück zu verkaufen
    verkauf_data = {
        'projekt_id': 1,
        'artikelnummer': 'TEST-001',
        'verkaufte_menge': 10,
        'verkaufspreis': 79.99
    }
    
    response = client_with_auth.auth.authenticated_post('/api/verkauf', json=verkauf_data)
    assert response.status_code == 400
    assert 'nicht genügend' in response.get_json()['error'].lower()

def test_verkauf_missing_fields(client_with_auth):
    # Ohne Projekt-ID
    response = client_with_auth.auth.authenticated_post('/api/verkauf', json={
        'artikelnummer': 'TEST-001',
        'verkaufte_menge': 1,
        'verkaufspreis': 79.99
    })
    assert response.status_code == 400
    assert 'error' in response.get_json()

def test_verkauf_fifo_principle(client_with_auth):
    # Mehrere Lagereingänge zu verschiedenen Preisen und Zeiten
    eingaenge = [
        {'menge': 10, 'einkaufspreis': 45.00, 'einlagerungsdatum': '2024-01-10'},
        {'menge': 10, 'einkaufspreis': 50.00, 'einlagerungsdatum': '2024-01-15'},
        {'menge': 10, 'einkaufspreis': 55.00, 'einlagerungsdatum': '2024-01-20'}
    ]
    
    for eingang in eingaenge:
        client_with_auth.auth.authenticated_post('/api/lager/eingang', json={
            'artikelnummer': 'TEST-001',
            **eingang
        })
    
    # 15 Stück verkaufen (sollte 10 vom ersten + 5 vom zweiten Eingang nehmen)
    response = client_with_auth.auth.authenticated_post('/api/verkauf', json={
        'projekt_id': 1,
        'artikelnummer': 'TEST-001',
        'verkaufte_menge': 15,
        'verkaufspreis': 79.99
    })
    assert response.status_code == 201
    
    # Verbleibenden Bestand prüfen (mit Zero-Einträgen)
    response = client_with_auth.auth.authenticated_get('/api/lager/bestand/TEST-001?include_zero=true')
    bestaende = response.get_json()
    
    # Erster Bestand sollte 0 sein
    # Zweiter Bestand sollte 5 sein (10 - 5)
    # Dritter Bestand sollte 10 sein (unverändert)
    verfuegbar = [b['verfuegbare_menge'] for b in sorted(bestaende, key=lambda x: x['einlagerungsdatum'])]
    assert verfuegbar == [0, 5, 10]

def test_verkauf_complete_stock_depletion(client_with_auth):
    # Lagereingang
    client_with_auth.auth.authenticated_post('/api/lager/eingang', json={
        'artikelnummer': 'TEST-001',
        'menge': 10,
        'einkaufspreis': 49.99
    })
    
    # Kompletten Bestand verkaufen
    response = client_with_auth.auth.authenticated_post('/api/verkauf', json={
        'projekt_id': 1,
        'artikelnummer': 'TEST-001',
        'verkaufte_menge': 10,
        'verkaufspreis': 79.99
    })
    assert response.status_code == 201
    
    # Bestand sollte leer sein
    response = client_with_auth.auth.authenticated_get('/api/lager/bestand')
    assert response.get_json() == []

def test_verkauf_invalid_projekt(client_with_auth):
    # Lagereingang
    client_with_auth.auth.authenticated_post('/api/lager/eingang', json={
        'artikelnummer': 'TEST-001',
        'menge': 5,
        'einkaufspreis': 49.99
    })
    
    # Verkauf mit ungültiger Projekt-ID
    response = client_with_auth.auth.authenticated_post('/api/verkauf', json={
        'projekt_id': 999,
        'artikelnummer': 'TEST-001',
        'verkaufte_menge': 1,
        'verkaufspreis': 79.99
    })
    assert response.status_code == 400

def test_multiple_verkaeufe_same_projekt(client_with_auth):
    # Lagereingang
    client_with_auth.auth.authenticated_post('/api/lager/eingang', json={
        'artikelnummer': 'TEST-001',
        'menge': 20,
        'einkaufspreis': 49.99
    })
    
    # Mehrere Verkäufe
    verkaeufe = [
        {'verkaufte_menge': 3, 'verkaufspreis': 75.00},
        {'verkaufte_menge': 5, 'verkaufspreis': 80.00},
        {'verkaufte_menge': 2, 'verkaufspreis': 82.00}
    ]
    
    for verkauf in verkaeufe:
        response = client_with_auth.auth.authenticated_post('/api/verkauf', json={
            'projekt_id': 1,
            'artikelnummer': 'TEST-001',
            **verkauf
        })
        assert response.status_code == 201
    
    # Projekt-Details prüfen
    response = client_with_auth.auth.authenticated_get(f'/api/projekte/{1}')
    projekt_data = response.get_json()
    assert len(projekt_data['verkaeufe']) == 3
    
    # Berechnung: 3*75 + 5*80 + 2*82 = 225 + 400 + 164 = 789
    assert projekt_data['gesamtumsatz'] == 789.0