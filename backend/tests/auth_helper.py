"""
Authentication Helper für Tests
Stellt gemeinsame Auth-Funktionen für alle Tests bereit
"""

import json
import os
import sys
import pytest

# Projekt-Root zum Python-Pfad hinzufügen
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, auth_service


class AuthHelper:
    """Helper-Klasse für Authentication in Tests"""
    
    def __init__(self, client):
        self.client = client
        self.test_user = {
            'username': 'testuser',
            'password': 'password123'
        }
        self.access_token = None
        self.refresh_token = None
    
    def setup_test_auth(self):
        """Setup für Test-Authentication - erstellt User und loggt ein"""
        # Test-User erstellen
        register_response = self.client.post('/api/auth/register',
                                           data=json.dumps(self.test_user),
                                           content_type='application/json')
        
        if register_response.status_code != 201:
            raise Exception(f"User-Erstellung fehlgeschlagen: {register_response.status_code}")
        
        # User einloggen
        login_response = self.client.post('/api/auth/login',
                                        data=json.dumps(self.test_user),
                                        content_type='application/json')
        
        if login_response.status_code != 200:
            raise Exception(f"Login fehlgeschlagen: {login_response.status_code}")
        
        tokens = login_response.get_json()
        self.access_token = tokens['access_token']
        self.refresh_token = tokens['refresh_token']
    
    def get_auth_headers(self):
        """Gibt Authorization-Headers für API-Calls zurück"""
        if not self.access_token:
            self.setup_test_auth()
        
        return {'Authorization': f'Bearer {self.access_token}'}
    
    def authenticated_get(self, url, **kwargs):
        """GET-Request mit Authentication"""
        headers = kwargs.pop('headers', {})
        headers.update(self.get_auth_headers())
        return self.client.get(url, headers=headers, **kwargs)
    
    def authenticated_post(self, url, **kwargs):
        """POST-Request mit Authentication"""
        headers = kwargs.pop('headers', {})
        headers.update(self.get_auth_headers())
        return self.client.post(url, headers=headers, **kwargs)
    
    def authenticated_put(self, url, **kwargs):
        """PUT-Request mit Authentication"""
        headers = kwargs.pop('headers', {})
        headers.update(self.get_auth_headers())
        return self.client.put(url, headers=headers, **kwargs)
    
    def authenticated_delete(self, url, **kwargs):
        """DELETE-Request mit Authentication"""
        headers = kwargs.pop('headers', {})
        headers.update(self.get_auth_headers())
        return self.client.delete(url, headers=headers, **kwargs)


@pytest.fixture
def auth_helper(client):
    """Pytest-Fixture für AuthHelper"""
    helper = AuthHelper(client)
    helper.setup_test_auth()
    return helper


@pytest.fixture  
def client_with_auth():
    """Pytest-Fixture für Test-Client mit Authentication"""
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        # Test-Datenbank setup
        test_db = "test_with_auth.db"
        if os.path.exists(test_db):
            os.remove(test_db)
        
        # AuthService mit Test-DB konfigurieren
        auth_service.db.db_path = test_db
        auth_service.db.init_database()
        
        # AuthHelper erstellen und Setup
        helper = AuthHelper(client)
        helper.setup_test_auth()
        
        # Client mit AuthHelper erweitern
        client.auth = helper
        
        yield client
        
        # Cleanup
        if os.path.exists(test_db):
            os.remove(test_db)


def create_test_data(client_with_auth):
    """Erstellt Standard-Testdaten für Tests"""
    auth = client_with_auth.auth
    
    # Lieferant erstellen
    lieferant_data = {
        'name': 'Test Lieferant',
        'kontakt': 'test@lieferant.de'
    }
    lieferant_response = auth.authenticated_post('/api/lieferanten', 
                                               data=json.dumps(lieferant_data),
                                               content_type='application/json')
    
    lieferant_id = lieferant_response.get_json()['id']
    
    # Artikel erstellen
    artikel_data = {
        'artikelnummer': 'TEST-001',
        'bezeichnung': 'Test Artikel',
        'lieferant_id': lieferant_id,
        'mindestmenge': 5
    }
    auth.authenticated_post('/api/artikel',
                          data=json.dumps(artikel_data),
                          content_type='application/json')
    
    # Kunde erstellen
    kunde_data = {
        'name': 'Test Kunde',
        'kontakt': 'test@kunde.de'
    }
    kunde_response = auth.authenticated_post('/api/kunden',
                                           data=json.dumps(kunde_data),
                                           content_type='application/json')
    
    kunde_id = kunde_response.get_json()['id']
    
    # Projekt erstellen
    projekt_data = {
        'projektname': 'Test Projekt',
        'kunde_id': kunde_id
    }
    projekt_response = auth.authenticated_post('/api/projekte',
                                             data=json.dumps(projekt_data),
                                             content_type='application/json')
    
    return {
        'lieferant_id': lieferant_id,
        'artikel_nummer': 'TEST-001',
        'kunde_id': kunde_id,
        'projekt_id': projekt_response.get_json()['id']
    }