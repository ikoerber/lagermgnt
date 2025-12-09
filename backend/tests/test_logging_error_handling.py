import pytest
import sys
import os
import sqlite3
from unittest.mock import patch

# Projekt-Root zum Python-Pfad hinzufügen
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from inventory_manager import InventoryManager
from exceptions import (
    ValidationError, NotFoundError, IntegrityError, 
    LieferantError, ArtikelError, DatabaseError
)
from logger_config import app_logger


class TestLoggingAndErrorHandling:
    
    def setup_method(self):
        """Test-Datenbank für jeden Test erstellen"""
        self.test_db = "test_logging.db"
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        self.inventory = InventoryManager()
        self.inventory.db.db_path = self.test_db
        self.inventory.db.init_database()
    
    def teardown_method(self):
        """Test-Datenbank nach jedem Test löschen"""
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    # Validierungstests
    def test_lieferant_empty_name_validation(self):
        """Test: Leerer Lieferantenname löst ValidationError aus"""
        with pytest.raises(ValidationError, match="Lieferantenname darf nicht leer sein"):
            self.inventory.lieferant_hinzufuegen("")
        
        with pytest.raises(ValidationError, match="Lieferantenname darf nicht leer sein"):
            self.inventory.lieferant_hinzufuegen("   ")
    
    def test_artikel_validation_errors(self):
        """Test: Artikel-Validierungsfehler"""
        # Erst Lieferant hinzufügen
        lieferant_id = self.inventory.lieferant_hinzufuegen("Test Lieferant")
        
        # Leere Artikelnummer
        with pytest.raises(ValidationError, match="Artikelnummer darf nicht leer sein"):
            self.inventory.artikel_hinzufuegen("", "Test Artikel", lieferant_id)
        
        # Leere Bezeichnung
        with pytest.raises(ValidationError, match="Artikelbezeichnung darf nicht leer sein"):
            self.inventory.artikel_hinzufuegen("ART-001", "", lieferant_id)
        
        # Ungültige Lieferanten-ID
        with pytest.raises(ValidationError, match="Ungültige Lieferanten-ID"):
            self.inventory.artikel_hinzufuegen("ART-001", "Test Artikel", 0)
        
        # Negative Mindestmenge
        with pytest.raises(ValidationError, match="Mindestmenge darf nicht negativ sein"):
            self.inventory.artikel_hinzufuegen("ART-001", "Test Artikel", lieferant_id, -1)
    
    def test_not_found_errors(self):
        """Test: NotFoundError für nicht existierende Ressourcen"""
        # Nicht existierender Lieferant
        with pytest.raises(NotFoundError, match="Lieferant mit ID 999 nicht gefunden"):
            self.inventory.lieferant_aktualisieren(999, "Test Name")
        
        with pytest.raises(NotFoundError, match="Lieferant mit ID 999 nicht gefunden"):
            self.inventory.lieferant_loeschen(999)
        
        # Nicht existierender Lieferant bei Artikel-Erstellung
        with pytest.raises(NotFoundError, match="Lieferant mit ID 999 nicht gefunden"):
            self.inventory.artikel_hinzufuegen("ART-001", "Test Artikel", 999)
    
    def test_integrity_error_on_lieferant_deletion(self):
        """Test: IntegrityError beim Löschen von Lieferant mit zugeordneten Artikeln"""
        # Lieferant und Artikel hinzufügen
        lieferant_id = self.inventory.lieferant_hinzufuegen("Test Lieferant")
        self.inventory.artikel_hinzufuegen("ART-001", "Test Artikel", lieferant_id)
        
        # Versuch Lieferant zu löschen sollte IntegrityError auslösen
        with pytest.raises(IntegrityError, match="Lieferant kann nicht gelöscht werden: 1 Artikel sind zugeordnet"):
            self.inventory.lieferant_loeschen(lieferant_id)
    
    def test_duplicate_lieferant_error(self):
        """Test: LieferantError bei doppelten Namen"""
        self.inventory.lieferant_hinzufuegen("Duplicate Supplier")
        
        with pytest.raises(LieferantError, match="Lieferant 'Duplicate Supplier' existiert bereits"):
            self.inventory.lieferant_hinzufuegen("Duplicate Supplier")
    
    def test_duplicate_artikel_error(self):
        """Test: ArtikelError bei doppelten Artikelnummern"""
        lieferant_id = self.inventory.lieferant_hinzufuegen("Test Lieferant")
        self.inventory.artikel_hinzufuegen("ART-001", "Test Artikel", lieferant_id)
        
        with pytest.raises(ArtikelError, match="Artikel 'ART-001' existiert bereits"):
            self.inventory.artikel_hinzufuegen("ART-001", "Anderer Artikel", lieferant_id)
    
    @patch('database.sqlite3.connect')
    def test_database_connection_error(self, mock_connect):
        """Test: DatabaseError bei Verbindungsfehlern"""
        mock_connect.side_effect = sqlite3.Error("Connection failed")
        
        with pytest.raises(DatabaseError, match="Datenbankverbindung fehlgeschlagen"):
            test_inventory = InventoryManager()
            test_inventory.db.get_connection()
    
    def test_logging_structure(self):
        """Test: Strukturiertes Logging funktioniert"""
        with patch('inventory_manager.app_logger') as mock_logger:
            # Operation die Logging auslöst
            lieferant_id = self.inventory.lieferant_hinzufuegen("Test Lieferant für Log")
            
            # Prüfen ob Log-Calls gemacht wurden
            mock_logger.info.assert_called()
            
            # Prüfen ob der richtige Inhalt geloggt wurde
            calls = mock_logger.info.call_args_list
            assert any("Füge Lieferant hinzu: Test Lieferant für Log" in str(call) for call in calls)
            assert any(f"Lieferant erfolgreich hinzugefügt: ID {lieferant_id}" in str(call) for call in calls)
    
    def test_error_logging_on_exceptions(self):
        """Test: Error-Logging bei Exceptions"""
        with patch('logger_config.app_logger') as mock_logger:
            try:
                self.inventory.lieferant_hinzufuegen("")
            except ValidationError:
                pass  # Erwarteter Fehler
            
            # Es sollte kein Error-Log für Validierungsfehler geben (das ist Warning-Level)
            # Aber für andere Fehler schon
            
    def test_whitespace_trimming(self):
        """Test: Whitespace wird korrekt entfernt"""
        lieferant_id = self.inventory.lieferant_hinzufuegen("  Test Lieferant  ")
        lieferanten = self.inventory.lieferanten_auflisten()
        
        # Name sollte getrimmt sein
        assert lieferanten[0].name == "Test Lieferant"
        
        # Gleiches für Artikel
        self.inventory.artikel_hinzufuegen("  ART-001  ", "  Test Artikel  ", lieferant_id)
        artikel = self.inventory.artikel_finden("ART-001")
        assert artikel.bezeichnung == "Test Artikel"