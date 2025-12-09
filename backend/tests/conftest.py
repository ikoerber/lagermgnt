import pytest
import os
import tempfile
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, inventory, reports
from database import Database

@pytest.fixture
def client():
    # Temporäre Datenbank erstellen
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    app.config['TESTING'] = True
    
    # Globale Instanzen für Tests patchen
    test_database = Database(db_path)
    inventory.db = test_database
    reports.db = test_database
    
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
def sample_data(client):
    # Lieferant anlegen
    lieferant_response = client.post('/api/lieferanten', json={
        'name': 'Test Möbel GmbH',
        'kontakt': 'test@moebel.de'
    })
    assert lieferant_response.status_code == 201
    lieferant_data = lieferant_response.get_json()
    assert 'id' in lieferant_data
    lieferant_id = lieferant_data['id']
    
    # Artikel anlegen
    artikel_response = client.post('/api/artikel', json={
        'artikelnummer': 'TEST-001',
        'bezeichnung': 'Test Stuhl',
        'lieferant_id': lieferant_id
    })
    assert artikel_response.status_code == 201
    
    # Kunde anlegen
    kunde_response = client.post('/api/kunden', json={
        'name': 'Test Kunde GmbH',
        'kontakt': 'kunde@test.de'
    })
    assert kunde_response.status_code == 201
    kunde_data = kunde_response.get_json()
    assert 'id' in kunde_data
    kunde_id = kunde_data['id']
    
    # Projekt anlegen
    projekt_response = client.post('/api/projekte', json={
        'projektname': 'Test Projekt',
        'kunde_id': kunde_id
    })
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