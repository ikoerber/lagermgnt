import pytest
from datetime import datetime

def test_lagereingang_success(client, sample_data):
    data = {
        'artikelnummer': sample_data['artikelnummer'],
        'menge': 10,
        'einkaufspreis': 49.99,
        'einlagerungsdatum': '2024-01-15'
    }
    
    response = client.post('/api/lager/eingang', json=data)
    assert response.status_code == 201
    
    response_data = response.get_json()
    assert response_data['message'] == 'Lagereingang erfolgreich'
    assert response_data['artikelnummer'] == data['artikelnummer']
    assert response_data['menge'] == data['menge']
    assert response_data['einkaufspreis'] == data['einkaufspreis']
    assert response_data['einlagerungsdatum'] == data['einlagerungsdatum']

def test_lagereingang_without_date(client, sample_data):
    data = {
        'artikelnummer': sample_data['artikelnummer'],
        'menge': 5,
        'einkaufspreis': 39.99
    }
    
    response = client.post('/api/lager/eingang', json=data)
    assert response.status_code == 201
    
    response_data = response.get_json()
    # Sollte heutiges Datum verwenden
    assert response_data['einlagerungsdatum'] == datetime.now().strftime("%Y-%m-%d")

def test_lagereingang_missing_fields(client):
    # Ohne Artikelnummer
    response = client.post('/api/lager/eingang', json={
        'menge': 10,
        'einkaufspreis': 49.99
    })
    assert response.status_code == 400
    assert 'error' in response.get_json()

def test_lagereingang_invalid_artikel(client):
    data = {
        'artikelnummer': 'NICHT-VORHANDEN',
        'menge': 10,
        'einkaufspreis': 49.99
    }
    
    response = client.post('/api/lager/eingang', json=data)
    assert response.status_code == 404
    assert 'error' in response.get_json()

def test_get_lagerbestand_returns_list(client):
    response = client.get('/api/lager/bestand')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_get_lagerbestand_after_eingang(client, sample_data):
    # Lagereingang buchen
    client.post('/api/lager/eingang', json={
        'artikelnummer': sample_data['artikelnummer'],
        'menge': 10,
        'einkaufspreis': 49.99
    })
    
    response = client.get('/api/lager/bestand')
    assert response.status_code == 200
    
    bestand = response.get_json()
    assert len(bestand) == 1
    assert bestand[0]['artikelnummer'] == sample_data['artikelnummer']
    assert bestand[0]['gesamtmenge'] == 10
    assert bestand[0]['durchschnittspreis'] == 49.99

def test_get_artikel_lagerbestand_success(client, sample_data):
    # Mehrere Eingänge mit verschiedenen Preisen
    eingaenge = [
        {'menge': 10, 'einkaufspreis': 49.99, 'einlagerungsdatum': '2024-01-10'},
        {'menge': 5, 'einkaufspreis': 54.99, 'einlagerungsdatum': '2024-01-15'}
    ]
    
    for eingang in eingaenge:
        client.post('/api/lager/eingang', json={
            'artikelnummer': sample_data['artikelnummer'],
            **eingang
        })
    
    response = client.get(f'/api/lager/bestand/{sample_data["artikelnummer"]}')
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

def test_get_artikel_lagerbestand_not_found(client):
    response = client.get('/api/lager/bestand/NICHT-VORHANDEN')
    assert response.status_code == 200
    assert response.get_json() == []

def test_multiple_lagereingang_same_artikel(client, sample_data):
    # Mehrere Eingänge für denselben Artikel
    eingaenge = [
        {'menge': 10, 'einkaufspreis': 45.00},
        {'menge': 15, 'einkaufspreis': 50.00},
        {'menge': 8, 'einkaufspreis': 48.00}
    ]
    
    for eingang in eingaenge:
        response = client.post('/api/lager/eingang', json={
            'artikelnummer': sample_data['artikelnummer'],
            **eingang
        })
        assert response.status_code == 201
    
    # Gesamtbestand prüfen
    response = client.get('/api/lager/bestand')
    bestand = response.get_json()
    assert len(bestand) == 1
    assert bestand[0]['gesamtmenge'] == 33  # 10 + 15 + 8
    
    # Detailbestand prüfen
    response = client.get(f'/api/lager/bestand/{sample_data["artikelnummer"]}')
    bestaende = response.get_json()
    assert len(bestaende) == 3