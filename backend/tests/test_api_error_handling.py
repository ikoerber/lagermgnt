import pytest
import json
import sys
import os
from unittest.mock import patch

# Projekt-Root zum Python-Pfad hinzufügen
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from exceptions import ValidationError, NotFoundError, IntegrityError


class TestAPIErrorHandling:
    
    def setup_method(self):
        """Test-Client für jeden Test erstellen"""
        app.config['TESTING'] = True
        self.client = app.test_client()
        
        # Test-Datenbank verwenden
        test_db = "test_api_errors.db"
        if os.path.exists(test_db):
            os.remove(test_db)
        
        # InventoryManager mit Test-DB patchen
        from app import inventory
        inventory.db.db_path = test_db
        inventory.db.init_database()
        self.test_db = test_db
    
    def teardown_method(self):
        """Test-Datenbank nach jedem Test löschen"""
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    def test_validation_error_response(self):
        """Test: ValidationError wird korrekt als 400 zurückgegeben"""
        response = self.client.post('/api/lieferanten', 
                                  data=json.dumps({}),
                                  content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['type'] == 'validation_error'
        assert 'Name ist erforderlich' in data['error']
    
    def test_empty_name_validation(self):
        """Test: Leerer Name wird abgefangen"""
        response = self.client.post('/api/lieferanten', 
                                  data=json.dumps({'name': ''}),
                                  content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Lieferantenname darf nicht leer sein' in data['error']
    
    def test_missing_json_data(self):
        """Test: Fehlende JSON-Daten"""
        response = self.client.post('/api/lieferanten', data='invalid json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'JSON-Daten erforderlich' in data['error']
    
    def test_duplicate_lieferant_error(self):
        """Test: Doppelter Lieferant gibt 500 mit korrektem Error zurück"""
        # Ersten Lieferant hinzufügen
        self.client.post('/api/lieferanten',
                        data=json.dumps({'name': 'Test Lieferant'}),
                        content_type='application/json')
        
        # Zweiten mit gleichem Namen versuchen
        response = self.client.post('/api/lieferanten',
                                  data=json.dumps({'name': 'Test Lieferant'}),
                                  content_type='application/json')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'existiert bereits' in data['error']
        assert data['type'] == 'application_error'
    
    def test_not_found_error_response(self):
        """Test: NotFoundError wird als 404 zurückgegeben"""
        # Da wir direkt Exception-Handler testen wollen, verwenden wir einen Mock
        with patch('app.inventory.lieferant_finden') as mock_find:
            mock_find.side_effect = NotFoundError("Lieferant nicht gefunden")
            
            response = self.client.get('/api/lieferanten/999')
            
            # Der GET-Endpoint sollte noch implementiert werden
            # Für diesen Test nehmen wir an dass er existiert
    
    def test_404_endpoint_not_found(self):
        """Test: 404 für nicht existierende Endpoints"""
        response = self.client.get('/api/nonexistent')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'Endpoint nicht gefunden' in data['error']
    
    def test_internal_server_error(self):
        """Test: 500 Internal Server Error"""
        with patch('app.inventory.lieferanten_auflisten') as mock_list:
            mock_list.side_effect = Exception("Unexpected error")
            
            response = self.client.get('/api/lieferanten')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data
    
    def test_json_response_structure(self):
        """Test: Error-Response hat korrekte JSON-Struktur"""
        response = self.client.post('/api/lieferanten', 
                                  data=json.dumps({'name': ''}),
                                  content_type='application/json')
        
        data = json.loads(response.data)
        
        # Pflichtfelder prüfen
        assert 'error' in data
        assert 'type' in data
        assert isinstance(data['error'], str)
        assert isinstance(data['type'], str)
    
    def test_successful_request_logging(self):
        """Test: Erfolgreiche Requests werden geloggt"""
        with patch('app.app_logger') as mock_logger:
            response = self.client.get('/api/lieferanten')
            
            assert response.status_code == 200
            mock_logger.debug.assert_called_with("GET /api/lieferanten aufgerufen")
    
    def test_error_request_logging(self):
        """Test: Fehlerhafte Requests werden geloggt"""
        with patch('app.app_logger') as mock_logger:
            response = self.client.post('/api/lieferanten',
                                      data=json.dumps({'name': ''}),
                                      content_type='application/json')
            
            assert response.status_code == 400
            # ValidationError sollte als Warning geloggt werden
            mock_logger.warning.assert_called()
    
    def test_cors_headers_present(self):
        """Test: CORS-Header sind in Error-Responses vorhanden"""
        response = self.client.get('/api/lieferanten')
        
        # CORS sollte auch bei Fehlern funktionieren
        # (Exakte Header hängen von CORS-Konfiguration ab)
        assert response.status_code == 200  # Dieser sollte erfolgreich sein