import pytest
import os
import tempfile
import sys
import json
import uuid

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set test environment before importing app
os.environ['FLASK_ENV'] = 'testing'

from app import app, auth_service
from inventory_manager import InventoryManager
from reports import ReportGenerator
from database import Database

@pytest.fixture
def client():
    # Temporäre Datenbank erstellen
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    
    # Test-Instanzen erstellen
    test_database = Database(db_path)
    
    # Create fresh instances for this test
    test_inventory = InventoryManager()
    test_inventory.db = test_database
    test_reports = ReportGenerator()
    test_reports.db = test_database
    test_auth_service = auth_service.__class__()  # Create fresh instance
    test_auth_service.db = test_database
    
    # Patch the blueprint modules for each test
    import api.auth
    import api.lieferanten
    import api.artikel
    import api.kunden
    import api.projekte
    import api.lager
    import api.verkauf
    import api.berichte
    
    # Store original instances to restore later
    original_instances = {
        'auth_service': api.auth.auth_service,
        'lieferanten_inventory': api.lieferanten.inventory,
        'artikel_inventory': api.artikel.inventory,
        'kunden_inventory': api.kunden.inventory,
        'projekte_inventory': api.projekte.inventory,
        'projekte_reports': api.projekte.reports,
        'lager_inventory': api.lager.inventory,
        'verkauf_inventory': api.verkauf.inventory,
        'berichte_inventory': api.berichte.inventory,
        'berichte_reports': api.berichte.reports,
    }
    
    # Patch all blueprint modules with test instances
    api.auth.auth_service = test_auth_service
    api.lieferanten.inventory = test_inventory
    api.artikel.inventory = test_inventory
    api.kunden.inventory = test_inventory
    api.projekte.inventory = test_inventory
    api.projekte.reports = test_reports
    api.lager.inventory = test_inventory
    api.verkauf.inventory = test_inventory
    api.berichte.inventory = test_inventory
    api.berichte.reports = test_reports
    
    with app.test_client() as client:
        yield client
    
    # Restore original instances
    api.auth.auth_service = original_instances['auth_service']
    api.lieferanten.inventory = original_instances['lieferanten_inventory']
    api.artikel.inventory = original_instances['artikel_inventory']
    api.kunden.inventory = original_instances['kunden_inventory']
    api.projekte.inventory = original_instances['projekte_inventory']
    api.projekte.reports = original_instances['projekte_reports']
    api.lager.inventory = original_instances['lager_inventory']
    api.verkauf.inventory = original_instances['verkauf_inventory']
    api.berichte.inventory = original_instances['berichte_inventory']
    api.berichte.reports = original_instances['berichte_reports']
    
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
    # Create test user with unique username per test
    unique_username = f'testuser_{uuid.uuid4().hex[:8]}'
    user_data = {
        'username': unique_username,
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