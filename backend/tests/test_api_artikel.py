import pytest

def test_get_artikel_returns_list(auth_client):
    response = auth_client.get('/api/artikel', headers=auth_client.auth_headers)
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_create_artikel_success(auth_client):
    # Erst Lieferant anlegen
    lieferant_response = auth_client.post('/api/lieferanten', json={
        'name': 'Test Lieferant',
        'kontakt': 'test@test.de'
    }, headers=auth_client.auth_headers)
    lieferant_id = lieferant_response.get_json()['id']
    
    # Dann Artikel anlegen
    artikel_data = {
        'artikelnummer': 'STUHL-001',
        'bezeichnung': 'Bürostuhl schwarz',
        'lieferant_id': lieferant_id
    }
    
    response = auth_client.post('/api/artikel', json=artikel_data, headers=auth_client.auth_headers)
    assert response.status_code == 201
    
    response_data = response.get_json()
    assert response_data['artikelnummer'] == artikel_data['artikelnummer']
    assert response_data['bezeichnung'] == artikel_data['bezeichnung']
    assert response_data['lieferant_id'] == artikel_data['lieferant_id']

def test_create_artikel_missing_fields(auth_client):
    # Unvollständige Daten
    response = auth_client.post('/api/artikel', json={
        'artikelnummer': 'TEST-001'
    }, headers=auth_client.auth_headers)
    assert response.status_code == 400
    assert 'error' in response.get_json()

def test_create_artikel_duplicate_artikelnummer(auth_client, sample_data):
    # Versuch, Artikel mit gleicher Nummer nochmal anzulegen (TEST-001 already exists in sample_data)
    response = auth_client.post('/api/artikel', json={
        'artikelnummer': 'TEST-001',
        'bezeichnung': 'Anderer Stuhl',
        'lieferant_id': sample_data['lieferant_id']
    }, headers=auth_client.auth_headers)
    assert response.status_code == 500  # ArtikelError for duplicate
    assert 'error' in response.get_json()

def test_create_artikel_invalid_lieferant(auth_client):
    response = auth_client.post('/api/artikel', json={
        'artikelnummer': 'INVALID-001',
        'bezeichnung': 'Test Artikel',
        'lieferant_id': 999
    }, headers=auth_client.auth_headers)
    assert response.status_code == 404  # NotFoundError for invalid lieferant

def test_get_artikel_after_create(auth_client, sample_data):
    response = auth_client.get('/api/artikel', headers=auth_client.auth_headers)
    assert response.status_code == 200
    
    artikel = response.get_json()
    assert len(artikel) >= 1
    artikel_nummern = [a['artikelnummer'] for a in artikel]
    assert 'TEST-001' in artikel_nummern

def test_get_artikel_by_nummer_success(auth_client, sample_data):
    response = auth_client.get('/api/artikel/TEST-001', headers=auth_client.auth_headers)
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['artikelnummer'] == 'TEST-001'
    assert data['bezeichnung'] == 'Test Stuhl'
    assert data['lieferant_id'] == sample_data['lieferant_id']

def test_get_artikel_by_nummer_not_found(auth_client):
    response = auth_client.get('/api/artikel/NICHT-VORHANDEN', headers=auth_client.auth_headers)
    assert response.status_code == 404
    assert 'error' in response.get_json()

def test_create_multiple_artikel_same_lieferant(auth_client):
    # Lieferant anlegen
    lieferant_response = auth_client.post('/api/lieferanten', json={
        'name': 'Multi Artikel Lieferant'
    }, headers=auth_client.auth_headers)
    lieferant_id = lieferant_response.get_json()['id']
    
    # Mehrere Artikel anlegen
    artikel_data = [
        {'artikelnummer': 'A001', 'bezeichnung': 'Artikel 1', 'lieferant_id': lieferant_id},
        {'artikelnummer': 'A002', 'bezeichnung': 'Artikel 2', 'lieferant_id': lieferant_id},
        {'artikelnummer': 'A003', 'bezeichnung': 'Artikel 3', 'lieferant_id': lieferant_id}
    ]
    
    for artikel in artikel_data:
        response = auth_client.post('/api/artikel', json=artikel, headers=auth_client.auth_headers)
        assert response.status_code == 201
    
    # Alle Artikel abrufen
    response = auth_client.get('/api/artikel', headers=auth_client.auth_headers)
    assert response.status_code == 200
    artikel_liste = response.get_json()
    
    # Prüfen dass unsere 3 Artikel dabei sind
    unsere_artikel = [a for a in artikel_liste if a['lieferant_name'] == 'Multi Artikel Lieferant']
    assert len(unsere_artikel) == 3