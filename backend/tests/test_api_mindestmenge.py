import pytest
from auth_helper import client_with_auth

def test_create_artikel_with_mindestmenge(client_with_auth):
    """Test creating article with specific minimum quantity"""
    response = client_with_auth.auth.authenticated_post('/api/artikel', json={
        'artikelnummer': 'MIN-001',
        'bezeichnung': 'Artikel mit Mindestmenge',
        'lieferant_id': 1,
        'mindestmenge': 5
    })
    assert response.status_code == 201
    
    data = response.get_json()
    assert data['artikelnummer'] == 'MIN-001'
    assert data['mindestmenge'] == 5

def test_create_artikel_default_mindestmenge(client_with_auth):
    """Test creating article with default minimum quantity"""
    response = client_with_auth.auth.authenticated_post('/api/artikel', json={
        'artikelnummer': 'DEF-001',
        'bezeichnung': 'Artikel mit Standard Mindestmenge',
        'lieferant_id': 1
    })
    assert response.status_code == 201
    
    data = response.get_json()
    assert data['mindestmenge'] == 1  # Default value

def test_get_artikel_includes_mindestmenge(client_with_auth):
    """Test that article list includes minimum quantity"""
    # Create article with specific minimum quantity
    client_with_auth.auth.authenticated_post('/api/artikel', json={
        'artikelnummer': 'INC-001',
        'bezeichnung': 'Artikel für Auflistung',
        'lieferant_id': 1,
        'mindestmenge': 10
    })
    
    response = client_with_auth.auth.authenticated_get('/api/artikel')
    assert response.status_code == 200
    
    articles = response.get_json()
    # Find our created article
    test_article = next((a for a in articles if a['artikelnummer'] == 'INC-001'), None)
    assert test_article is not None
    assert test_article['mindestmenge'] == 10

def test_get_artikel_detail_includes_mindestmenge(client_with_auth):
    """Test that article detail includes minimum quantity"""
    # Create article with specific minimum quantity
    client_with_auth.auth.authenticated_post('/api/artikel', json={
        'artikelnummer': 'DET-001',
        'bezeichnung': 'Artikel für Detail',
        'lieferant_id': 1,
        'mindestmenge': 15
    })
    
    response = client_with_auth.auth.authenticated_get('/api/artikel/DET-001')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['mindestmenge'] == 15

def test_get_artikel_unter_mindestmenge_empty(client_with_auth):
    """Test minimum quantity report when no articles are below minimum"""
    response = client_with_auth.auth.authenticated_get('/api/berichte/mindestmenge')
    assert response.status_code == 200
    assert response.get_json() == []

def test_get_artikel_unter_mindestmenge_with_data(client_with_auth):
    """Test minimum quantity report with articles below minimum"""
    # Create article with minimum quantity of 10
    client_with_auth.auth.authenticated_post('/api/artikel', json={
        'artikelnummer': 'LOW-001',
        'bezeichnung': 'Artikel unter Mindestmenge',
        'lieferant_id': 1,
        'mindestmenge': 10
    })
    
    # Add only 5 pieces to inventory (below minimum)
    client_with_auth.auth.authenticated_post('/api/lager/eingang', json={
        'artikelnummer': 'LOW-001',
        'menge': 5,
        'einkaufspreis': 25.00
    })
    
    response = client_with_auth.auth.authenticated_get('/api/berichte/mindestmenge')
    assert response.status_code == 200
    
    data = response.get_json()
    
    # Find our specific article in the report
    low_article = next((a for a in data if a['artikelnummer'] == 'LOW-001'), None)
    assert low_article is not None
    assert low_article['mindestmenge'] == 10
    assert low_article['aktueller_bestand'] == 5
    assert low_article['nachbestellmenge'] == 5  # 10 - 5

def test_artikel_above_mindestmenge_not_in_report(client_with_auth):
    """Test that articles above minimum quantity are not in the report"""
    # Create article with minimum quantity of 5
    client_with_auth.auth.authenticated_post('/api/artikel', json={
        'artikelnummer': 'HIGH-001',
        'bezeichnung': 'Artikel über Mindestmenge',
        'lieferant_id': 1,
        'mindestmenge': 5
    })
    
    # Add 10 pieces to inventory (above minimum)
    client_with_auth.auth.authenticated_post('/api/lager/eingang', json={
        'artikelnummer': 'HIGH-001',
        'menge': 10,
        'einkaufspreis': 30.00
    })
    
    response = client_with_auth.auth.authenticated_get('/api/berichte/mindestmenge')
    assert response.status_code == 200
    
    data = response.get_json()
    # Should not contain our article
    assert not any(a['artikelnummer'] == 'HIGH-001' for a in data)

def test_artikel_at_mindestmenge_not_in_report(client_with_auth):
    """Test that articles exactly at minimum quantity are not in the report"""
    # Create article with minimum quantity of 7
    client_with_auth.auth.authenticated_post('/api/artikel', json={
        'artikelnummer': 'EXACT-001',
        'bezeichnung': 'Artikel genau bei Mindestmenge',
        'lieferant_id': 1,
        'mindestmenge': 7
    })
    
    # Add exactly 7 pieces to inventory
    client_with_auth.auth.authenticated_post('/api/lager/eingang', json={
        'artikelnummer': 'EXACT-001',
        'menge': 7,
        'einkaufspreis': 35.00
    })
    
    response = client_with_auth.auth.authenticated_get('/api/berichte/mindestmenge')
    assert response.status_code == 200
    
    data = response.get_json()
    # Should not contain our article
    assert not any(a['artikelnummer'] == 'EXACT-001' for a in data)

def test_mindestmenge_after_sales(client_with_auth):
    """Test minimum quantity report after sales reduce inventory below minimum"""
    # Create article with minimum quantity of 8
    client_with_auth.auth.authenticated_post('/api/artikel', json={
        'artikelnummer': 'SALES-001',
        'bezeichnung': 'Artikel für Verkaufstest',
        'lieferant_id': 1,
        'mindestmenge': 8
    })
    
    # Add 12 pieces to inventory
    client_with_auth.auth.authenticated_post('/api/lager/eingang', json={
        'artikelnummer': 'SALES-001',
        'menge': 12,
        'einkaufspreis': 40.00
    })
    
    # Sell 7 pieces, leaving 5 (below minimum of 8)
    client_with_auth.auth.authenticated_post('/api/verkauf', json={
        'projekt_id': sample_data['projekt_id'],
        'artikelnummer': 'SALES-001',
        'verkaufte_menge': 7,
        'verkaufspreis': 60.00
    })
    
    response = client_with_auth.auth.authenticated_get('/api/berichte/mindestmenge')
    assert response.status_code == 200
    
    data = response.get_json()
    
    # Find our article in the report
    sales_article = next((a for a in data if a['artikelnummer'] == 'SALES-001'), None)
    assert sales_article is not None
    assert sales_article['mindestmenge'] == 8
    assert sales_article['aktueller_bestand'] == 5
    assert sales_article['nachbestellmenge'] == 3  # 8 - 5

def test_multiple_artikel_under_mindestmenge(client_with_auth):
    """Test minimum quantity report with multiple articles below minimum"""
    # Create first article
    client_with_auth.auth.authenticated_post('/api/artikel', json={
        'artikelnummer': 'MULTI-001',
        'bezeichnung': 'Erster Artikel unter Mindestmenge',
        'lieferant_id': 1,
        'mindestmenge': 6
    })
    
    # Create second article  
    client_with_auth.auth.authenticated_post('/api/artikel', json={
        'artikelnummer': 'MULTI-002',
        'bezeichnung': 'Zweiter Artikel unter Mindestmenge',
        'lieferant_id': 1,
        'mindestmenge': 4
    })
    
    # Add inventory below minimum for both
    client_with_auth.auth.authenticated_post('/api/lager/eingang', json={
        'artikelnummer': 'MULTI-001',
        'menge': 3,
        'einkaufspreis': 20.00
    })
    
    client_with_auth.auth.authenticated_post('/api/lager/eingang', json={
        'artikelnummer': 'MULTI-002',
        'menge': 2,
        'einkaufspreis': 15.00
    })
    
    response = client_with_auth.auth.authenticated_get('/api/berichte/mindestmenge')
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