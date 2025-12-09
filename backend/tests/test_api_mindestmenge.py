import pytest

def test_create_artikel_with_mindestmenge(auth_client, sample_data):
    """Test creating article with specific minimum quantity"""
    response = auth_client.post('/api/artikel', json={
        'artikelnummer': 'MIN-001',
        'bezeichnung': 'Artikel mit Mindestmenge',
        'lieferant_id': sample_data['lieferant_id'],
        'mindestmenge': 5
    }, headers=auth_client.auth_headers)
    assert response.status_code == 201
    
    data = response.get_json()
    assert data['artikelnummer'] == 'MIN-001'
    assert data['mindestmenge'] == 5

def test_create_artikel_default_mindestmenge(auth_client, sample_data):
    """Test creating article with default minimum quantity"""
    response = auth_client.post('/api/artikel', json={
        'artikelnummer': 'DEF-001',
        'bezeichnung': 'Artikel mit Standard Mindestmenge',
        'lieferant_id': sample_data['lieferant_id']
    }, headers=auth_client.auth_headers)
    assert response.status_code == 201
    
    data = response.get_json()
    assert data['mindestmenge'] == 1  # Default value

def test_get_artikel_includes_mindestmenge(auth_client, sample_data):
    """Test that article list includes minimum quantity"""
    # Create article with specific minimum quantity
    auth_client.post('/api/artikel', json={
        'artikelnummer': 'INC-001',
        'bezeichnung': 'Artikel für Auflistung',
        'lieferant_id': sample_data['lieferant_id'],
        'mindestmenge': 10
    }, headers=auth_client.auth_headers)
    
    response = auth_client.get('/api/artikel', headers=auth_client.auth_headers)
    assert response.status_code == 200
    
    articles = response.get_json()
    # Find our created article
    test_article = next((a for a in articles if a['artikelnummer'] == 'INC-001'), None)
    assert test_article is not None
    assert test_article['mindestmenge'] == 10

def test_get_artikel_detail_includes_mindestmenge(auth_client, sample_data):
    """Test that article detail includes minimum quantity"""
    # Create article with specific minimum quantity
    auth_client.post('/api/artikel', json={
        'artikelnummer': 'DET-001',
        'bezeichnung': 'Artikel für Detail',
        'lieferant_id': sample_data['lieferant_id'],
        'mindestmenge': 15
    }, headers=auth_client.auth_headers)
    
    response = auth_client.get('/api/artikel/DET-001', headers=auth_client.auth_headers)
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['mindestmenge'] == 15

def test_get_artikel_unter_mindestmenge_empty(auth_client):
    """Test minimum quantity report when no articles are below minimum"""
    response = auth_client.get('/api/berichte/mindestmenge', headers=auth_client.auth_headers)
    assert response.status_code == 200
    assert response.get_json() == []

def test_get_artikel_unter_mindestmenge_with_data(auth_client, sample_data):
    """Test minimum quantity report with articles below minimum"""
    # Create article with minimum quantity of 10
    auth_client.post('/api/artikel', json={
        'artikelnummer': 'LOW-001',
        'bezeichnung': 'Artikel unter Mindestmenge',
        'lieferant_id': sample_data['lieferant_id'],
        'mindestmenge': 10
    }, headers=auth_client.auth_headers)
    
    # Add only 5 pieces to inventory (below minimum)
    auth_client.post('/api/lager/eingang', json={
        'artikelnummer': 'LOW-001',
        'menge': 5,
        'einkaufspreis': 25.00
    }, headers=auth_client.auth_headers)
    
    response = auth_client.get('/api/berichte/mindestmenge', headers=auth_client.auth_headers)
    assert response.status_code == 200
    
    data = response.get_json()
    
    # Find our specific article in the report
    low_article = next((a for a in data if a['artikelnummer'] == 'LOW-001'), None)
    assert low_article is not None
    assert low_article['mindestmenge'] == 10
    assert low_article['aktueller_bestand'] == 5
    assert low_article['nachbestellmenge'] == 5  # 10 - 5

def test_artikel_above_mindestmenge_not_in_report(auth_client, sample_data):
    """Test that articles above minimum quantity are not in the report"""
    # Create article with minimum quantity of 5
    auth_client.post('/api/artikel', json={
        'artikelnummer': 'HIGH-001',
        'bezeichnung': 'Artikel über Mindestmenge',
        'lieferant_id': sample_data['lieferant_id'],
        'mindestmenge': 5
    }, headers=auth_client.auth_headers)
    
    # Add 10 pieces to inventory (above minimum)
    auth_client.post('/api/lager/eingang', json={
        'artikelnummer': 'HIGH-001',
        'menge': 10,
        'einkaufspreis': 30.00
    }, headers=auth_client.auth_headers)
    
    response = auth_client.get('/api/berichte/mindestmenge', headers=auth_client.auth_headers)
    assert response.status_code == 200
    
    data = response.get_json()
    # Should not contain our article
    assert not any(a['artikelnummer'] == 'HIGH-001' for a in data)

def test_artikel_at_mindestmenge_not_in_report(auth_client, sample_data):
    """Test that articles exactly at minimum quantity are not in the report"""
    # Create article with minimum quantity of 7
    auth_client.post('/api/artikel', json={
        'artikelnummer': 'EXACT-001',
        'bezeichnung': 'Artikel genau bei Mindestmenge',
        'lieferant_id': sample_data['lieferant_id'],
        'mindestmenge': 7
    }, headers=auth_client.auth_headers)
    
    # Add exactly 7 pieces to inventory
    auth_client.post('/api/lager/eingang', json={
        'artikelnummer': 'EXACT-001',
        'menge': 7,
        'einkaufspreis': 35.00
    }, headers=auth_client.auth_headers)
    
    response = auth_client.get('/api/berichte/mindestmenge', headers=auth_client.auth_headers)
    assert response.status_code == 200
    
    data = response.get_json()
    # Should not contain our article
    assert not any(a['artikelnummer'] == 'EXACT-001' for a in data)

def test_mindestmenge_after_sales(auth_client, sample_data):
    """Test minimum quantity report after sales reduce inventory below minimum"""
    # Create article with minimum quantity of 8
    auth_client.post('/api/artikel', json={
        'artikelnummer': 'SALES-001',
        'bezeichnung': 'Artikel für Verkaufstest',
        'lieferant_id': sample_data['lieferant_id'],
        'mindestmenge': 8
    }, headers=auth_client.auth_headers)
    
    # Add 12 pieces to inventory
    auth_client.post('/api/lager/eingang', json={
        'artikelnummer': 'SALES-001',
        'menge': 12,
        'einkaufspreis': 40.00
    }, headers=auth_client.auth_headers)
    
    # Sell 7 pieces, leaving 5 (below minimum of 8)
    auth_client.post('/api/verkauf', json={
        'projekt_id': sample_data['projekt_id'],
        'artikelnummer': 'SALES-001',
        'verkaufte_menge': 7,
        'verkaufspreis': 60.00
    }, headers=auth_client.auth_headers)
    
    response = auth_client.get('/api/berichte/mindestmenge', headers=auth_client.auth_headers)
    assert response.status_code == 200
    
    data = response.get_json()
    
    # Find our article in the report
    sales_article = next((a for a in data if a['artikelnummer'] == 'SALES-001'), None)
    assert sales_article is not None
    assert sales_article['mindestmenge'] == 8
    assert sales_article['aktueller_bestand'] == 5
    assert sales_article['nachbestellmenge'] == 3  # 8 - 5

def test_multiple_artikel_under_mindestmenge(auth_client, sample_data):
    """Test minimum quantity report with multiple articles below minimum"""
    # Create first article
    auth_client.post('/api/artikel', json={
        'artikelnummer': 'MULTI-001',
        'bezeichnung': 'Erster Artikel unter Mindestmenge',
        'lieferant_id': sample_data['lieferant_id'],
        'mindestmenge': 6
    }, headers=auth_client.auth_headers)
    
    # Create second article  
    auth_client.post('/api/artikel', json={
        'artikelnummer': 'MULTI-002',
        'bezeichnung': 'Zweiter Artikel unter Mindestmenge',
        'lieferant_id': sample_data['lieferant_id'],
        'mindestmenge': 4
    }, headers=auth_client.auth_headers)
    
    # Add inventory below minimum for both
    auth_client.post('/api/lager/eingang', json={
        'artikelnummer': 'MULTI-001',
        'menge': 3,
        'einkaufspreis': 20.00
    }, headers=auth_client.auth_headers)
    
    auth_client.post('/api/lager/eingang', json={
        'artikelnummer': 'MULTI-002',
        'menge': 2,
        'einkaufspreis': 15.00
    }, headers=auth_client.auth_headers)
    
    response = auth_client.get('/api/berichte/mindestmenge', headers=auth_client.auth_headers)
    assert response.status_code == 200
    
    data = response.get_json()
    assert len(data) >= 2
    
    # Find both articles
    multi1 = next((a for a in data if a['artikelnummer'] == 'MULTI-001'), None)
    multi2 = next((a for a in data if a['artikelnummer'] == 'MULTI-002'), None)
    
    assert multi1 is not None
    assert multi1['nachbestellmenge'] == 3  # 6 - 3
    
    assert multi2 is not None 
    assert multi2['nachbestellmenge'] == 2  # 4 - 2