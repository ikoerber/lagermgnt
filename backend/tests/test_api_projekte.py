import pytest
from auth_helper import client_with_auth

def test_get_projekte_returns_list(client_with_auth):
    response = client_with_auth.auth.authenticated_get('/api/projekte')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_create_projekt_success(client_with_auth):
    # Kunde anlegen
    kunde_response = client_with_auth.auth.authenticated_post('/api/kunden', json={
        'name': 'Projekt Kunde',
        'kontakt': 'projekt@kunde.de'
    })
    kunde_id = kunde_response.get_json()['id']
    
    # Projekt anlegen
    projekt_data = {
        'projektname': 'Großes Büroprojekt',
        'kunde_id': kunde_id
    }
    
    response = client_with_auth.auth.authenticated_post('/api/projekte', json=projekt_data)
    assert response.status_code == 201
    
    response_data = response.get_json()
    assert 'id' in response_data
    assert response_data['projektname'] == projekt_data['projektname']
    assert response_data['kunde_id'] == projekt_data['kunde_id']

def test_create_projekt_missing_fields(client_with_auth):
    # Ohne Projektname
    response = client_with_auth.auth.authenticated_post('/api/projekte', json={'kunde_id': 1})
    assert response.status_code == 400
    assert 'error' in response.get_json()
    
    # Ohne Kunde-ID
    response = client_with_auth.auth.authenticated_post('/api/projekte', json={'projektname': 'Test Projekt'})
    assert response.status_code == 400
    assert 'error' in response.get_json()

def test_create_projekt_invalid_kunde(client_with_auth):
    response = client_with_auth.auth.authenticated_post('/api/projekte', json={
        'projektname': 'Unmögliches Projekt',
        'kunde_id': 999
    })
    assert response.status_code == 400

def test_get_projekte_after_create(client_with_auth):
    # Kunde anlegen
    kunde_response = client_with_auth.auth.authenticated_post('/api/kunden', json={'name': 'Multi Projekt Kunde'})
    kunde_id = kunde_response.get_json()['id']
    
    # Mehrere Projekte anlegen
    projekte_data = [
        {'projektname': 'Projekt Alpha', 'kunde_id': kunde_id},
        {'projektname': 'Projekt Beta', 'kunde_id': kunde_id}
    ]
    
    for projekt in projekte_data:
        response = client_with_auth.auth.authenticated_post('/api/projekte', json=projekt)
        assert response.status_code == 201
    
    response = client_with_auth.auth.authenticated_get('/api/projekte')
    assert response.status_code == 200
    
    projekte = response.get_json()
    projekt_namen = [p['projektname'] for p in projekte]
    assert 'Projekt Alpha' in projekt_namen
    assert 'Projekt Beta' in projekt_namen
    
    # Prüfen dass beide Projekte zum richtigen Kunden gehören
    alpha_projekt = next(p for p in projekte if p['projektname'] == 'Projekt Alpha')
    assert alpha_projekt['kunde_name'] == 'Multi Projekt Kunde'

def test_get_projekt_detail_success(client_with_auth):
    response = client_with_auth.auth.authenticated_get(f'/api/projekte/{1}')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['projektname'] == 'Test Projekt'
    assert data['kunde'] == 'Test Kunde GmbH'
    assert 'verkaeufe' in data
    assert 'gesamtumsatz' in data
    assert data['gesamtumsatz'] == 0  # Noch keine Verkäufe

def test_get_projekt_detail_not_found(client_with_auth):
    response = client_with_auth.auth.authenticated_get('/api/projekte/999')
    assert response.status_code == 404
    assert 'error' in response.get_json()

def test_create_projekt_empty_body(client_with_auth):
    response = client_with_auth.auth.authenticated_post('/api/projekte', json={})
    assert response.status_code == 400