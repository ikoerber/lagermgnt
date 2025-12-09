import pytest

def test_get_lieferanten_empty_in_fresh_client(auth_client):
    """Test mit neuem Client ohne sample_data"""
    response = auth_client.get('/api/lieferanten', headers=auth_client.auth_headers)
    assert response.status_code == 200
    assert response.get_json() == []

def test_get_artikel_empty_in_fresh_client(auth_client):
    """Test mit neuem Client ohne sample_data"""
    response = auth_client.get('/api/artikel', headers=auth_client.auth_headers)
    assert response.status_code == 200
    assert response.get_json() == []

def test_get_kunden_empty_in_fresh_client(auth_client):
    """Test mit neuem Client ohne sample_data"""
    response = auth_client.get('/api/kunden', headers=auth_client.auth_headers)
    assert response.status_code == 200
    assert response.get_json() == []

def test_get_projekte_empty_in_fresh_client(auth_client):
    """Test mit neuem Client ohne sample_data"""
    response = auth_client.get('/api/projekte', headers=auth_client.auth_headers)
    assert response.status_code == 200
    assert response.get_json() == []

def test_get_lager_empty_in_fresh_client(auth_client):
    """Test mit neuem Client ohne sample_data"""
    response = auth_client.get('/api/lager/bestand', headers=auth_client.auth_headers)
    assert response.status_code == 200
    assert response.get_json() == []

def test_get_berichte_empty_in_fresh_client(auth_client):
    """Test mit neuem Client ohne sample_data"""
    response = auth_client.get('/api/berichte/lagerbestand', headers=auth_client.auth_headers)
    assert response.status_code == 200
    assert response.get_json() == []
    
    response = auth_client.get('/api/berichte/projekte', headers=auth_client.auth_headers)
    assert response.status_code == 200
    assert response.get_json() == []
    
    response = auth_client.get('/api/berichte/lagerumschlag', headers=auth_client.auth_headers)
    assert response.status_code == 200
    assert response.get_json() == []