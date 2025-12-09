import pytest

# Lieferanten CRUD Tests
def test_lieferanten_crud_operations(client):
    """Test complete CRUD operations for Lieferanten"""
    # CREATE
    response = client.post('/api/lieferanten', json={
        'name': 'CRUD Test Lieferant',
        'kontakt': 'crud@test.de'
    })
    assert response.status_code == 201
    lieferant_id = response.get_json()['id']
    
    # READ (detail)
    response = client.get(f'/api/lieferanten/{lieferant_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'CRUD Test Lieferant'
    assert data['kontakt'] == 'crud@test.de'
    
    # UPDATE
    response = client.put(f'/api/lieferanten/{lieferant_id}', json={
        'name': 'CRUD Test Lieferant Updated',
        'kontakt': 'updated@test.de'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'CRUD Test Lieferant Updated'
    assert data['kontakt'] == 'updated@test.de'
    
    # Verify UPDATE
    response = client.get(f'/api/lieferanten/{lieferant_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'CRUD Test Lieferant Updated'
    
    # DELETE
    response = client.delete(f'/api/lieferanten/{lieferant_id}')
    assert response.status_code == 200
    
    # Verify DELETE
    response = client.get(f'/api/lieferanten/{lieferant_id}')
    assert response.status_code == 404

def test_kunden_detail_operation(client):
    """Test Kunden detail read operation"""
    # CREATE
    response = client.post('/api/kunden', json={
        'name': 'Detail Test Kunde',
        'kontakt': 'detail@test.de'
    })
    assert response.status_code == 201
    kunde_id = response.get_json()['id']
    
    # READ (detail)
    response = client.get(f'/api/kunden/{kunde_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Detail Test Kunde'
    assert data['kontakt'] == 'detail@test.de'

def test_update_lieferant_not_found(client):
    """Test updating non-existent Lieferant"""
    response = client.put('/api/lieferanten/999999', json={
        'name': 'Non-existent Lieferant'
    })
    assert response.status_code == 404

def test_delete_lieferant_not_found(client):
    """Test deleting non-existent Lieferant"""
    response = client.delete('/api/lieferanten/999999')
    assert response.status_code == 404

def test_get_kunde_not_found(client):
    """Test getting non-existent Kunde"""
    response = client.get('/api/kunden/999999')
    assert response.status_code == 404

def test_update_lieferant_missing_name(client, sample_data):
    """Test updating Lieferant without name"""
    response = client.put(f'/api/lieferanten/{sample_data["lieferant_id"]}', json={
        'kontakt': 'only-contact@test.de'
    })
    assert response.status_code == 400
    assert 'Name ist erforderlich' in response.get_json()['error']

def test_update_lieferant_no_json(client, sample_data):
    """Test updating Lieferant without JSON data"""
    response = client.put(f'/api/lieferanten/{sample_data["lieferant_id"]}')
    assert response.status_code == 400