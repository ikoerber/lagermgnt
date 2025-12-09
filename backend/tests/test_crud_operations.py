import pytest

# Lieferanten CRUD Tests
def test_lieferanten_crud_operations(auth_client):
    """Test complete CRUD operations for Lieferanten"""
    # CREATE
    response = auth_client.post('/api/lieferanten', json={
        'name': 'CRUD Test Lieferant',
        'kontakt': 'crud@test.de'
    }, headers=auth_client.auth_headers)
    assert response.status_code == 201
    lieferant_id = response.get_json()['id']
    
    # READ (detail)
    response = auth_client.get(f'/api/lieferanten/{lieferant_id}', headers=auth_client.auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'CRUD Test Lieferant'
    assert data['kontakt'] == 'crud@test.de'
    
    # UPDATE
    response = auth_client.put(f'/api/lieferanten/{lieferant_id}', json={
        'name': 'CRUD Test Lieferant Updated',
        'kontakt': 'updated@test.de'
    }, headers=auth_client.auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'CRUD Test Lieferant Updated'
    assert data['kontakt'] == 'updated@test.de'
    
    # Verify UPDATE
    response = auth_client.get(f'/api/lieferanten/{lieferant_id}', headers=auth_client.auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'CRUD Test Lieferant Updated'
    
    # DELETE
    response = auth_client.delete(f'/api/lieferanten/{lieferant_id}', headers=auth_client.auth_headers)
    assert response.status_code == 200
    
    # Verify DELETE
    response = auth_client.get(f'/api/lieferanten/{lieferant_id}', headers=auth_client.auth_headers)
    assert response.status_code == 404

def test_kunden_detail_operation(auth_client):
    """Test Kunden detail read operation"""
    # CREATE
    response = auth_client.post('/api/kunden', json={
        'name': 'Detail Test Kunde',
        'kontakt': 'detail@test.de'
    }, headers=auth_client.auth_headers)
    assert response.status_code == 201
    kunde_id = response.get_json()['id']
    
    # READ (detail)
    response = auth_client.get(f'/api/kunden/{kunde_id}', headers=auth_client.auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Detail Test Kunde'
    assert data['kontakt'] == 'detail@test.de'

def test_update_lieferant_not_found(auth_client):
    """Test updating non-existent Lieferant"""
    response = auth_client.put('/api/lieferanten/999999', json={
        'name': 'Non-existent Lieferant'
    }, headers=auth_client.auth_headers)
    assert response.status_code == 404

def test_delete_lieferant_not_found(auth_client):
    """Test deleting non-existent Lieferant"""
    response = auth_client.delete('/api/lieferanten/999999', headers=auth_client.auth_headers)
    assert response.status_code == 404

def test_get_kunde_not_found(auth_client):
    """Test getting non-existent Kunde"""
    response = auth_client.get('/api/kunden/999999', headers=auth_client.auth_headers)
    assert response.status_code == 404

def test_update_lieferant_missing_name(auth_client):
    """Test updating Lieferant without name"""
    response = auth_client.put(f'/api/lieferanten/{1}', json={
        'kontakt': 'only-contact@test.de'
    }, headers=auth_client.auth_headers)
    assert response.status_code == 400
    assert 'Name ist erforderlich' in response.get_json()['error']

def test_update_lieferant_no_json(auth_client):
    """Test updating Lieferant without JSON data"""
    response = auth_client.put(f'/api/lieferanten/{1}', headers=auth_client.auth_headers)
    assert response.status_code == 400