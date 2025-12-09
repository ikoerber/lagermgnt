import pytest
import os
import tempfile
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set test environment before importing app
os.environ['FLASK_ENV'] = 'testing'

from app import app, inventory, reports, auth_service
from database import Database

@pytest.fixture
def client():
    # Temporäre Datenbank erstellen
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    
    # Globale Instanzen für Tests patchen
    test_database = Database(db_path)
    inventory.db = test_database
    reports.db = test_database
    auth_service.db = test_database
    
    with app.test_client() as client:
        yield client
    
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def test_db():
    db_fd, db_path = tempfile.mkstemp()
    test_database = Database(db_path)
    yield test_database
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def auth_client(client):
    """Client with authentication setup"""
    # Create test user
    user_data = {
        'username': 'testuser',
        'password': 'password123'
    }
    
    # Register user
    register_response = client.post('/api/auth/register', 
                                  data=json.dumps(user_data),
                                  content_type='application/json')
    assert register_response.status_code == 201
    
    # Login and get token
    login_response = client.post('/api/auth/login',
                               data=json.dumps(user_data),
                               content_type='application/json')
    assert login_response.status_code == 200
    
    tokens = login_response.get_json()
    access_token = tokens['access_token']
    
    # Add auth headers to client
    client.auth_headers = {'Authorization': f'Bearer {access_token}'}
    
    return client

@pytest.fixture
def sample_data(auth_client):
    headers = auth_client.auth_headers
    
    # Lieferant anlegen
    lieferant_response = auth_client.post('/api/lieferanten', 
                                        json={'name': 'Test Möbel GmbH', 'kontakt': 'test@moebel.de'},
                                        headers=headers)
    assert lieferant_response.status_code == 201
    lieferant_data = lieferant_response.get_json()
    assert 'id' in lieferant_data
    lieferant_id = lieferant_data['id']
    
    # Artikel anlegen
    artikel_response = auth_client.post('/api/artikel', 
                                      json={'artikelnummer': 'TEST-001', 'bezeichnung': 'Test Stuhl', 'lieferant_id': lieferant_id},
                                      headers=headers)
    assert artikel_response.status_code == 201
    
    # Kunde anlegen
    kunde_response = auth_client.post('/api/kunden', 
                                    json={'name': 'Test Kunde GmbH', 'kontakt': 'kunde@test.de'},
                                    headers=headers)
    assert kunde_response.status_code == 201
    kunde_data = kunde_response.get_json()
    assert 'id' in kunde_data
    kunde_id = kunde_data['id']
    
    # Projekt anlegen
    projekt_response = auth_client.post('/api/projekte', 
                                      json={'projektname': 'Test Projekt', 'kunde_id': kunde_id},
                                      headers=headers)
    assert projekt_response.status_code == 201
    projekt_data = projekt_response.get_json()
    assert 'id' in projekt_data
    projekt_id = projekt_data['id']
    
    return {
        'lieferant_id': lieferant_id,
        'kunde_id': kunde_id,
        'projekt_id': projekt_id,
        'artikelnummer': 'TEST-001'
    }