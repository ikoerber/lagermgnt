import pytest
from auth_helper import client_with_auth
import json

def test_get_lieferanten_returns_list(client_with_auth):
    response = client_with_auth.auth.authenticated_get('/api/lieferanten')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_create_lieferant_success(client_with_auth):
    data = {
        'name': 'Möbel Schmidt GmbH',
        'kontakt': 'info@schmidt.de'
    }
    response = client_with_auth.auth.authenticated_post('/api/lieferanten', json=data)
    assert response.status_code == 201
    
    response_data = response.get_json()
    assert 'id' in response_data
    assert response_data['name'] == data['name']
    assert response_data['kontakt'] == data['kontakt']

def test_create_lieferant_without_name(client_with_auth):
    data = {'kontakt': 'test@test.de'}
    response = client_with_auth.auth.authenticated_post('/api/lieferanten', json=data)
    assert response.status_code == 400
    assert 'error' in response.get_json()

def test_create_lieferant_empty_body(client_with_auth):
    response = client_with_auth.auth.authenticated_post('/api/lieferanten', json={})
    assert response.status_code == 400
    
def test_create_lieferant_no_json(client_with_auth):
    response = client_with_auth.auth.authenticated_post('/api/lieferanten')
    assert response.status_code == 400

def test_get_lieferanten_after_create(client_with_auth):
    # Ersten Lieferanten anlegen
    response1 = client_with_auth.auth.authenticated_post('/api/lieferanten', json={
        'name': 'Lieferant 1',
        'kontakt': 'l1@test.de'
    })
    assert response1.status_code == 201
    
    # Zweiten Lieferanten anlegen
    response2 = client_with_auth.auth.authenticated_post('/api/lieferanten', json={
        'name': 'Lieferant 2',
        'kontakt': 'l2@test.de'
    })
    assert response2.status_code == 201
    
    response = client_with_auth.auth.authenticated_get('/api/lieferanten')
    assert response.status_code == 200
    
    lieferanten = response.get_json()
    # Prüfen dass mindestens unsere 2 Lieferanten dabei sind
    lieferant_namen = [l['name'] for l in lieferanten]
    assert 'Lieferant 1' in lieferant_namen
    assert 'Lieferant 2' in lieferant_namen

def test_get_lieferant_by_id_success(client_with_auth):
    # Lieferanten anlegen
    create_response = client_with_auth.auth.authenticated_post('/api/lieferanten', json={
        'name': 'Test Lieferant',
        'kontakt': 'test@lieferant.de'
    })
    lieferant_id = create_response.get_json()['id']
    
    # Lieferanten abrufen
    response = client_with_auth.auth.authenticated_get(f'/api/lieferanten/{lieferant_id}')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['id'] == lieferant_id
    assert data['name'] == 'Test Lieferant'
    assert data['kontakt'] == 'test@lieferant.de'

def test_get_lieferant_by_id_not_found(client_with_auth):
    response = client_with_auth.auth.authenticated_get('/api/lieferanten/999')
    assert response.status_code == 404
    assert 'error' in response.get_json()

def test_create_lieferant_with_minimal_data(client_with_auth):
    data = {'name': 'Minimal Lieferant'}
    response = client_with_auth.auth.authenticated_post('/api/lieferanten', json=data)
    assert response.status_code == 201
    
    response_data = response.get_json()
    assert response_data['name'] == 'Minimal Lieferant'
    assert response_data['kontakt'] == ''