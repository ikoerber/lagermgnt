import pytest
import json

def test_get_lieferanten_returns_list(auth_client):
    response = auth_client.get('/api/lieferanten', headers=auth_client.auth_headers)
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_create_lieferant_success(auth_client):
    data = {
        'name': 'Möbel Schmidt GmbH',
        'kontakt': 'info@schmidt.de'
    }
    response = auth_client.post('/api/lieferanten', json=data, headers=auth_client.auth_headers)
    assert response.status_code == 201
    
    response_data = response.get_json()
    assert 'id' in response_data
    assert response_data['name'] == data['name']
    assert response_data['kontakt'] == data['kontakt']

def test_create_lieferant_without_name(auth_client):
    data = {'kontakt': 'test@test.de'}
    response = auth_client.post('/api/lieferanten', json=data, headers=auth_client.auth_headers)
    assert response.status_code == 400
    assert 'error' in response.get_json()

def test_create_lieferant_empty_body(auth_client):
    response = auth_client.post('/api/lieferanten', json={}, headers=auth_client.auth_headers)
    assert response.status_code == 400
    
def test_create_lieferant_no_json(auth_client):
    response = auth_client.post('/api/lieferanten', headers=auth_client.auth_headers)
    assert response.status_code == 400

def test_get_lieferanten_after_create(auth_client):
    # Ersten Lieferanten anlegen
    response1 = auth_client.post('/api/lieferanten', json={
        'name': 'Lieferant 1',
        'kontakt': 'l1@test.de'
    }, headers=auth_client.auth_headers)
    assert response1.status_code == 201
    
    # Zweiten Lieferanten anlegen
    response2 = auth_client.post('/api/lieferanten', json={
        'name': 'Lieferant 2',
        'kontakt': 'l2@test.de'
    }, headers=auth_client.auth_headers)
    assert response2.status_code == 201
    
    response = auth_client.get('/api/lieferanten', headers=auth_client.auth_headers)
    assert response.status_code == 200
    
    lieferanten = response.get_json()
    # Prüfen dass mindestens unsere 2 Lieferanten dabei sind
    lieferant_namen = [l['name'] for l in lieferanten]
    assert 'Lieferant 1' in lieferant_namen
    assert 'Lieferant 2' in lieferant_namen

def test_get_lieferant_by_id_success(auth_client):
    # Lieferanten anlegen
    create_response = auth_client.post('/api/lieferanten', json={
        'name': 'Test Lieferant',
        'kontakt': 'test@lieferant.de'
    }, headers=auth_client.auth_headers)
    lieferant_id = create_response.get_json()['id']
    
    # Lieferanten abrufen
    response = auth_client.get(f'/api/lieferanten/{lieferant_id}', headers=auth_client.auth_headers)
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['id'] == lieferant_id
    assert data['name'] == 'Test Lieferant'
    assert data['kontakt'] == 'test@lieferant.de'

def test_get_lieferant_by_id_not_found(auth_client):
    response = auth_client.get('/api/lieferanten/999', headers=auth_client.auth_headers)
    assert response.status_code == 404
    assert 'error' in response.get_json()

def test_create_lieferant_with_minimal_data(auth_client):
    data = {'name': 'Minimal Lieferant'}
    response = auth_client.post('/api/lieferanten', json=data, headers=auth_client.auth_headers)
    assert response.status_code == 201
    
    response_data = response.get_json()
    assert response_data['name'] == 'Minimal Lieferant'
    assert response_data['kontakt'] == ''