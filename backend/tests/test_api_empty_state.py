import pytest

def test_get_lieferanten_empty_in_fresh_client(client):
    """Test mit neuem Client ohne sample_data"""
    response = client.get('/api/lieferanten')
    assert response.status_code == 200
    assert response.get_json() == []

def test_get_artikel_empty_in_fresh_client(client):
    """Test mit neuem Client ohne sample_data"""
    response = client.get('/api/artikel')
    assert response.status_code == 200
    assert response.get_json() == []

def test_get_kunden_empty_in_fresh_client(client):
    """Test mit neuem Client ohne sample_data"""
    response = client.get('/api/kunden')
    assert response.status_code == 200
    assert response.get_json() == []

def test_get_projekte_empty_in_fresh_client(client):
    """Test mit neuem Client ohne sample_data"""
    response = client.get('/api/projekte')
    assert response.status_code == 200
    assert response.get_json() == []

def test_get_lager_empty_in_fresh_client(client):
    """Test mit neuem Client ohne sample_data"""
    response = client.get('/api/lager/bestand')
    assert response.status_code == 200
    assert response.get_json() == []

def test_get_berichte_empty_in_fresh_client(client):
    """Test mit neuem Client ohne sample_data"""
    response = client.get('/api/berichte/lagerbestand')
    assert response.status_code == 200
    assert response.get_json() == []
    
    response = client.get('/api/berichte/projekte')
    assert response.status_code == 200
    assert response.get_json() == []
    
    response = client.get('/api/berichte/lagerumschlag')
    assert response.status_code == 200
    assert response.get_json() == []