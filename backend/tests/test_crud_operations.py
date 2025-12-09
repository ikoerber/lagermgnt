import pytest
from auth_helper import client_with_auth

# Lieferanten CRUD Tests
def test_lieferanten_crud_operations(client_with_auth):
    """Test complete CRUD operations for Lieferanten"""
    # CREATE
    response = client_with_auth.auth.authenticated_post('/api/lieferanten', json={
        'name': 'CRUD Test Lieferant',
        'kontakt': 'crud@test.de'
    })
    assert response.status_code == 201
    lieferant_id = response.get_json()['id']
    
    # READ (detail)
    response = client_with_auth.auth.authenticated_get(f'/api/lieferanten/{lieferant_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'CRUD Test Lieferant'
    assert data['kontakt'] == 'crud@test.de'
    
    # UPDATE
    response = client_with_auth.auth.authenticated_put(f'/api/lieferanten/{lieferant_id}', json={
        'name': 'CRUD Test Lieferant Updated',
        'kontakt': 'updated@test.de'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'CRUD Test Lieferant Updated'
    assert data['kontakt'] == 'updated@test.de'
    
    # Verify UPDATE
    response = client_with_auth.auth.authenticated_get(f'/api/lieferanten/{lieferant_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'CRUD Test Lieferant Updated'
    
    # DELETE
    response = client_with_auth.auth.authenticated_delete(f'/api/lieferanten/{lieferant_id}')
    assert response.status_code == 200
    
    # Verify DELETE
    response = client_with_auth.auth.authenticated_get(f'/api/lieferanten/{lieferant_id}')
    assert response.status_code == 404

def test_kunden_detail_operation(client_with_auth):
    """Test Kunden detail read operation"""
    # CREATE
    response = client_with_auth.auth.authenticated_post('/api/kunden', json={
        'name': 'Detail Test Kunde',
        'kontakt': 'detail@test.de'
    })
    assert response.status_code == 201
    kunde_id = response.get_json()['id']
    
    # READ (detail)
    response = client_with_auth.auth.authenticated_get(f'/api/kunden/{kunde_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Detail Test Kunde'
    assert data['kontakt'] == 'detail@test.de'

def test_update_lieferant_not_found(client_with_auth):
    """Test updating non-existent Lieferant"""
    response = client_with_auth.auth.authenticated_put('/api/lieferanten/999999', json={
        'name': 'Non-existent Lieferant'
    })
    assert response.status_code == 404

def test_delete_lieferant_not_found(client_with_auth):
    """Test deleting non-existent Lieferant"""
    response = client_with_auth.auth.authenticated_delete('/api/lieferanten/999999')
    assert response.status_code == 404

def test_get_kunde_not_found(client_with_auth):
    """Test getting non-existent Kunde"""
    response = client_with_auth.auth.authenticated_get('/api/kunden/999999')
    assert response.status_code == 404

def test_update_lieferant_missing_name(client_with_auth):
    """Test updating Lieferant without name"""
    response = client_with_auth.auth.authenticated_put(f'/api/lieferanten/{1}', json={
        'kontakt': 'only-contact@test.de'
    })
    assert response.status_code == 400
    assert 'Name ist erforderlich' in response.get_json()['error']

def test_update_lieferant_no_json(client_with_auth):
    """Test updating Lieferant without JSON data"""
    response = client_with_auth.auth.authenticated_put(f'/api/lieferanten/{1}')
    assert response.status_code == 400