import pytest
from datetime import datetime

def test_lagereingang_success(auth_client, sample_data):
    data = {
        'artikelnummer': sample_data['artikelnummer'],
        'menge': 10,
        'einkaufspreis': 49.99,
        'einlagerungsdatum': '2024-01-15'
    }
    
    response = auth_client.post('/api/lager/eingang', json=data, headers=auth_client.auth_headers)
    assert response.status_code == 201
    
    response_data = response.get_json()
    assert response_data['message'] == 'Lagereingang erfolgreich'
    assert response_data['artikelnummer'] == data['artikelnummer']
    assert response_data['menge'] == data['menge']
    assert response_data['einkaufspreis'] == data['einkaufspreis']
    assert response_data['einlagerungsdatum'] == data['einlagerungsdatum']

def test_lagereingang_without_date(auth_client, sample_data):
    data = {
        'artikelnummer': sample_data['artikelnummer'],
        'menge': 5,
        'einkaufspreis': 39.99
    }
    
    response = auth_client.post('/api/lager/eingang', json=data, headers=auth_client.auth_headers)
    assert response.status_code == 201
    
    response_data = response.get_json()
    # Sollte heutiges Datum verwenden
    assert response_data['einlagerungsdatum'] == datetime.now().strftime("%Y-%m-%d")

def test_lagereingang_missing_fields(auth_client):
    # Ohne Artikelnummer
    response = auth_client.post('/api/lager/eingang', json={
        'menge': 10,
        'einkaufspreis': 49.99
    }, headers=auth_client.auth_headers)
    assert response.status_code == 400
    assert 'error' in response.get_json()

def test_lagereingang_invalid_artikel(auth_client):
    data = {
        'artikelnummer': 'NICHT-VORHANDEN',
        'menge': 10,
        'einkaufspreis': 49.99
    }
    
    response = auth_client.post('/api/lager/eingang', json=data, headers=auth_client.auth_headers)
    assert response.status_code == 404
    assert 'error' in response.get_json()

def test_get_lagerbestand_returns_list(auth_client):
    response = auth_client.get('/api/lager/bestand', headers=auth_client.auth_headers)
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_get_lagerbestand_after_eingang(auth_client, sample_data):
    # Lagereingang buchen
    auth_client.post('/api/lager/eingang', json={
        'artikelnummer': sample_data['artikelnummer'],
        'menge': 10,
        'einkaufspreis': 49.99
    }, headers=auth_client.auth_headers)
    
    response = auth_client.get('/api/lager/bestand', headers=auth_client.auth_headers)
    assert response.status_code == 200
    
    bestand = response.get_json()
    assert len(bestand) >= 1
    # Find our article in the response
    artikel_found = next((b for b in bestand if b['artikelnummer'] == sample_data['artikelnummer']), None)
    assert artikel_found is not None
    assert artikel_found['gesamtmenge'] == 10
    assert artikel_found['durchschnittspreis'] == 49.99

def test_get_artikel_lagerbestand_success(auth_client, sample_data):
    # Mehrere Eingänge mit verschiedenen Preisen
    eingaenge = [
        {'menge': 10, 'einkaufspreis': 49.99, 'einlagerungsdatum': '2024-01-10'},
        {'menge': 5, 'einkaufspreis': 54.99, 'einlagerungsdatum': '2024-01-15'}
    ]
    
    for eingang in eingaenge:
        auth_client.post('/api/lager/eingang', json={
            'artikelnummer': sample_data['artikelnummer'],
            **eingang
        }, headers=auth_client.auth_headers)
    
    response = auth_client.get(f'/api/lager/bestand/{sample_data["artikelnummer"]}', headers=auth_client.auth_headers)
    assert response.status_code == 200
    
    bestaende = response.get_json()
    assert len(bestaende) == 2
    
    # Sollte nach Datum sortiert sein (FIFO)
    assert bestaende[0]['einlagerungsdatum'] == '2024-01-10'
    assert bestaende[0]['verfuegbare_menge'] == 10
    assert bestaende[0]['einkaufspreis'] == 49.99
    
    assert bestaende[1]['einlagerungsdatum'] == '2024-01-15'
    assert bestaende[1]['verfuegbare_menge'] == 5
    assert bestaende[1]['einkaufspreis'] == 54.99

def test_get_artikel_lagerbestand_not_found(auth_client):
    response = auth_client.get('/api/lager/bestand/NICHT-VORHANDEN', headers=auth_client.auth_headers)
    assert response.status_code == 200
    assert response.get_json() == []

def test_multiple_lagereingang_same_artikel(auth_client, sample_data):
    # Mehrere Eingänge für denselben Artikel
    eingaenge = [
        {'menge': 10, 'einkaufspreis': 45.00},
        {'menge': 15, 'einkaufspreis': 50.00},
        {'menge': 8, 'einkaufspreis': 48.00}
    ]
    
    for eingang in eingaenge:
        response = auth_client.post('/api/lager/eingang', json={
            'artikelnummer': sample_data['artikelnummer'],
            **eingang
        }, headers=auth_client.auth_headers)
        assert response.status_code == 201
    
    # Gesamtbestand prüfen
    response = auth_client.get('/api/lager/bestand', headers=auth_client.auth_headers)
    bestand = response.get_json()
    assert len(bestand) >= 1
    artikel_found = next((b for b in bestand if b['artikelnummer'] == sample_data['artikelnummer']), None)
    assert artikel_found is not None
    assert artikel_found['gesamtmenge'] == 33  # 10 + 15 + 8
    
    # Detailbestand prüfen
    response = auth_client.get(f'/api/lager/bestand/{sample_data["artikelnummer"]}', headers=auth_client.auth_headers)
    bestaende = response.get_json()
    assert len(bestaende) == 3