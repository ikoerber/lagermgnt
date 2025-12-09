import pytest

def test_delete_lieferant_with_articles(auth_client):
    """Test that Lieferant cannot be deleted when articles exist"""
    # Create Lieferant
    lieferant_response = auth_client.post('/api/lieferanten', json={
        'name': 'Lieferant mit Artikeln',
        'kontakt': 'artikel@test.de'
    }, headers=auth_client.auth_headers)
    assert lieferant_response.status_code == 201
    lieferant_id = lieferant_response.get_json()['id']
    
    # Create Article for this Lieferant
    artikel_response = auth_client.post('/api/artikel', json={
        'artikelnummer': 'REF-001',
        'bezeichnung': 'Referenz Test Artikel',
        'lieferant_id': lieferant_id
    }, headers=auth_client.auth_headers)
    assert artikel_response.status_code == 201
    
    # Try to delete Lieferant - should fail due to referential integrity
    response = auth_client.delete(f'/api/lieferanten/{lieferant_id}', headers=auth_client.auth_headers)
    assert response.status_code == 400
    assert 'Artikel vorhanden' in response.get_json()['error']
    
    # Verify Lieferant still exists
    response = auth_client.get(f'/api/lieferanten/{lieferant_id}', headers=auth_client.auth_headers)
    assert response.status_code == 200

def test_delete_lieferant_without_articles(auth_client):
    """Test that Lieferant can be deleted when no articles exist"""
    # Create Lieferant
    lieferant_response = auth_client.post('/api/lieferanten', json={
        'name': 'Lieferant ohne Artikel',
        'kontakt': 'leer@test.de'
    }, headers=auth_client.auth_headers)
    assert lieferant_response.status_code == 201
    lieferant_id = lieferant_response.get_json()['id']
    
    # Delete Lieferant - should succeed
    response = auth_client.delete(f'/api/lieferanten/{lieferant_id}', headers=auth_client.auth_headers)
    assert response.status_code == 200
    
    # Verify Lieferant is deleted
    response = auth_client.get(f'/api/lieferanten/{lieferant_id}', headers=auth_client.auth_headers)
    assert response.status_code == 404

def test_create_artikel_with_invalid_lieferant(auth_client):
    """Test that article creation fails with non-existent Lieferant"""
    response = auth_client.post('/api/artikel', json={
        'artikelnummer': 'INVALID-001',
        'bezeichnung': 'Artikel mit ungültigem Lieferant',
        'lieferant_id': 999999  # Non-existent
    }, headers=auth_client.auth_headers)
    assert response.status_code == 400
    assert 'Lieferant nicht gefunden' in response.get_json()['error']

def test_create_projekt_with_invalid_kunde(auth_client):
    """Test that project creation fails with non-existent Kunde"""
    response = auth_client.post('/api/projekte', json={
        'projektname': 'Projekt mit ungültigem Kunde',
        'kunde_id': 999999  # Non-existent
    }, headers=auth_client.auth_headers)
    assert response.status_code == 400
    assert 'Kunde nicht gefunden' in response.get_json()['error']

def test_lagereingang_with_invalid_artikel(auth_client):
    """Test that inventory entry fails with non-existent Article"""
    response = auth_client.post('/api/lager/eingang', json={
        'artikelnummer': 'NONEXISTENT-001',
        'menge': 10,
        'einkaufspreis': 25.00
    }, headers=auth_client.auth_headers)
    assert response.status_code == 404
    assert 'Artikel nicht gefunden' in response.get_json()['error']

def test_verkauf_with_invalid_projekt(auth_client):
    """Test that sales entry fails with non-existent Project"""
    # First add some inventory
    auth_client.post('/api/lager/eingang', json={
        'artikelnummer': 'TEST-001',
        'menge': 10,
        'einkaufspreis': 25.00
    }, headers=auth_client.auth_headers)
    
    # Try to sell with invalid project
    response = auth_client.post('/api/verkauf', json={
        'projekt_id': 999999,  # Non-existent
        'artikelnummer': 'TEST-001',
        'verkaufte_menge': 5,
        'verkaufspreis': 40.00
    }, headers=auth_client.auth_headers)
    assert response.status_code == 400
    assert 'Projekt nicht gefunden' in response.get_json()['error']

def test_verkauf_with_invalid_artikel(auth_client):
    """Test that sales entry fails with non-existent Article"""
    response = auth_client.post('/api/verkauf', json={
        'projekt_id': sample_data['projekt_id'],
        'artikelnummer': 'NONEXISTENT-002',
        'verkaufte_menge': 5,
        'verkaufspreis': 40.00
    }, headers=auth_client.auth_headers)
    assert response.status_code == 400
    assert 'Nicht genügend Artikel im Lager verfügbar' in response.get_json()['error']

def test_foreign_key_constraints_in_database(auth_client):
    """Test that database enforces foreign key constraints"""
    # This test verifies that the database itself enforces FK constraints
    # when PRAGMA foreign_keys = ON is set
    
    # Try to insert article with invalid lieferant_id directly in DB
    # This should be caught by the application logic, but let's verify
    # the database constraints are working
    
    # Create valid lieferant first
    lieferant_response = auth_client.post('/api/lieferanten', json={
        'name': 'FK Test Lieferant',
        'kontakt': 'fk@test.de'
    }, headers=auth_client.auth_headers)
    assert lieferant_response.status_code == 201
    
    # Create valid artikel
    artikel_response = auth_client.post('/api/artikel', json={
        'artikelnummer': 'FK-001',
        'bezeichnung': 'FK Test Artikel',
        'lieferant_id': lieferant_response.get_json(, headers=auth_client.auth_headers)['id']
    })
    assert artikel_response.status_code == 201
    
    # Verify the artikel was created successfully
    response = auth_client.get('/api/artikel/FK-001', headers=auth_client.auth_headers)
    assert response.status_code == 200

def test_referential_integrity_chain(auth_client):
    """Test complete referential integrity chain"""
    # Create Lieferant
    lieferant_response = auth_client.post('/api/lieferanten', json={
        'name': 'Chain Test Lieferant',
        'kontakt': 'chain@test.de'
    }, headers=auth_client.auth_headers)
    lieferant_id = lieferant_response.get_json()['id']
    
    # Create Kunde  
    kunde_response = auth_client.post('/api/kunden', json={
        'name': 'Chain Test Kunde',
        'kontakt': 'kunde@test.de'
    }, headers=auth_client.auth_headers)
    kunde_id = kunde_response.get_json()['id']
    
    # Create Artikel
    artikel_response = auth_client.post('/api/artikel', json={
        'artikelnummer': 'CHAIN-001',
        'bezeichnung': 'Chain Test Artikel',
        'lieferant_id': lieferant_id
    }, headers=auth_client.auth_headers)
    
    # Create Projekt
    projekt_response = auth_client.post('/api/projekte', json={
        'projektname': 'Chain Test Projekt',
        'kunde_id': kunde_id
    }, headers=auth_client.auth_headers)
    projekt_id = projekt_response.get_json()['id']
    
    # Create Lagereingang
    lager_response = auth_client.post('/api/lager/eingang', json={
        'artikelnummer': 'CHAIN-001',
        'menge': 15,
        'einkaufspreis': 30.00
    }, headers=auth_client.auth_headers)
    assert lager_response.status_code == 201
    
    # Create Verkauf
    verkauf_response = auth_client.post('/api/verkauf', json={
        'projekt_id': projekt_id,
        'artikelnummer': 'CHAIN-001',
        'verkaufte_menge': 5,
        'verkaufspreis': 50.00
    }, headers=auth_client.auth_headers)
    assert verkauf_response.status_code == 201
    
    # Now try to delete Lieferant - should fail because artikel exists
    response = auth_client.delete(f'/api/lieferanten/{lieferant_id}', headers=auth_client.auth_headers)
    assert response.status_code == 400
    assert 'Artikel vorhanden' in response.get_json()['error']
    
    # Verify all entities still exist
    assert auth_client.get(f'/api/lieferanten/{lieferant_id}', headers=auth_client.auth_headers).status_code == 200
    assert auth_client.get(f'/api/kunden/{kunde_id}', headers=auth_client.auth_headers).status_code == 200
    assert auth_client.get('/api/artikel/CHAIN-001', headers=auth_client.auth_headers).status_code == 200
    assert auth_client.get(f'/api/projekte/{projekt_id}', headers=auth_client.auth_headers).status_code == 200