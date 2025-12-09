import pytest

def test_get_artikel_returns_list(client):
    response = client.get('/api/artikel')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_create_artikel_success(client):
    # Erst Lieferant anlegen
    lieferant_response = client.post('/api/lieferanten', json={
        'name': 'Test Lieferant',
        'kontakt': 'test@test.de'
    })
    lieferant_id = lieferant_response.get_json()['id']
    
    # Dann Artikel anlegen
    artikel_data = {
        'artikelnummer': 'STUHL-001',
        'bezeichnung': 'Bürostuhl schwarz',
        'lieferant_id': lieferant_id
    }
    
    response = client.post('/api/artikel', json=artikel_data)
    assert response.status_code == 201
    
    response_data = response.get_json()
    assert response_data['artikelnummer'] == artikel_data['artikelnummer']
    assert response_data['bezeichnung'] == artikel_data['bezeichnung']
    assert response_data['lieferant_id'] == artikel_data['lieferant_id']

def test_create_artikel_missing_fields(client):
    # Unvollständige Daten
    response = client.post('/api/artikel', json={
        'artikelnummer': 'TEST-001'
    })
    assert response.status_code == 400
    assert 'error' in response.get_json()

def test_create_artikel_duplicate_artikelnummer(client, sample_data):
    # Versuch, Artikel mit gleicher Nummer nochmal anzulegen
    response = client.post('/api/artikel', json={
        'artikelnummer': sample_data['artikelnummer'],
        'bezeichnung': 'Anderer Stuhl',
        'lieferant_id': sample_data['lieferant_id']
    })
    assert response.status_code == 400
    assert 'error' in response.get_json()

def test_create_artikel_invalid_lieferant(client):
    response = client.post('/api/artikel', json={
        'artikelnummer': 'INVALID-001',
        'bezeichnung': 'Test Artikel',
        'lieferant_id': 999
    })
    assert response.status_code == 400

def test_get_artikel_after_create(client, sample_data):
    response = client.get('/api/artikel')
    assert response.status_code == 200
    
    artikel = response.get_json()
    assert len(artikel) == 1
    assert artikel[0]['artikelnummer'] == sample_data['artikelnummer']
    assert artikel[0]['bezeichnung'] == 'Test Stuhl'
    assert artikel[0]['lieferant_name'] == 'Test Möbel GmbH'

def test_get_artikel_by_nummer_success(client, sample_data):
    response = client.get(f'/api/artikel/{sample_data["artikelnummer"]}')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['artikelnummer'] == sample_data['artikelnummer']
    assert data['bezeichnung'] == 'Test Stuhl'
    assert data['lieferant_id'] == sample_data['lieferant_id']

def test_get_artikel_by_nummer_not_found(client):
    response = client.get('/api/artikel/NICHT-VORHANDEN')
    assert response.status_code == 404
    assert 'error' in response.get_json()

def test_create_multiple_artikel_same_lieferant(client):
    # Lieferant anlegen
    lieferant_response = client.post('/api/lieferanten', json={
        'name': 'Multi Artikel Lieferant'
    })
    lieferant_id = lieferant_response.get_json()['id']
    
    # Mehrere Artikel anlegen
    artikel_data = [
        {'artikelnummer': 'A001', 'bezeichnung': 'Artikel 1', 'lieferant_id': lieferant_id},
        {'artikelnummer': 'A002', 'bezeichnung': 'Artikel 2', 'lieferant_id': lieferant_id},
        {'artikelnummer': 'A003', 'bezeichnung': 'Artikel 3', 'lieferant_id': lieferant_id}
    ]
    
    for artikel in artikel_data:
        response = client.post('/api/artikel', json=artikel)
        assert response.status_code == 201
    
    # Alle Artikel abrufen
    response = client.get('/api/artikel')
    assert response.status_code == 200
    artikel_liste = response.get_json()
    
    # Prüfen dass unsere 3 Artikel dabei sind
    unsere_artikel = [a for a in artikel_liste if a['lieferant_name'] == 'Multi Artikel Lieferant']
    assert len(unsere_artikel) == 3