from datetime import datetime
from typing import List, Optional
from database import Database
from models import Lieferant, Artikel, Kunde, Projekt, Lagerbestand, Verkauf
from logger_config import app_logger
from exceptions import (
    LieferantError, ArtikelError, LagerError, VerkaufError, 
    ValidationError, NotFoundError, IntegrityError, DatabaseError
)

class InventoryManager:
    def __init__(self):
        app_logger.info("Initialisiere InventoryManager")
        self.db = Database()
        app_logger.info("InventoryManager erfolgreich initialisiert")
    
    # Lieferanten Management
    def lieferant_hinzufuegen(self, name: str, kontakt: str = "") -> int:
        if not name or not name.strip():
            raise ValidationError("Lieferantenname darf nicht leer sein")
        
        name = name.strip()
        app_logger.info(f"Füge Lieferant hinzu: {name}")
        
        try:
            query = "INSERT INTO lieferanten (name, kontakt) VALUES (?, ?)"
            lieferant_id = self.db.execute_insert(query, (name, kontakt))
            app_logger.info(f"Lieferant erfolgreich hinzugefügt: ID {lieferant_id}")
            return lieferant_id
        except DatabaseError as e:
            if "UNIQUE constraint failed" in str(e):
                raise LieferantError(f"Lieferant '{name}' existiert bereits")
            raise LieferantError(f"Fehler beim Hinzufügen des Lieferanten: {e}")
    
    def lieferanten_auflisten(self) -> List[Lieferant]:
        query = "SELECT id, name, kontakt FROM lieferanten ORDER BY name"
        results = self.db.execute_query(query)
        return [Lieferant(id=row[0], name=row[1], kontakt=row[2]) for row in results]
    
    def lieferant_finden(self, lieferant_id: int) -> Optional[Lieferant]:
        query = "SELECT id, name, kontakt FROM lieferanten WHERE id = ?"
        results = self.db.execute_query(query, (lieferant_id,))
        if results:
            row = results[0]
            return Lieferant(id=row[0], name=row[1], kontakt=row[2])
        return None
    
    def lieferant_aktualisieren(self, lieferant_id: int, name: str, kontakt: str = "") -> bool:
        if not name or not name.strip():
            raise ValidationError("Lieferantenname darf nicht leer sein")
        if lieferant_id <= 0:
            raise ValidationError("Ungültige Lieferanten-ID")
        
        name = name.strip()
        app_logger.info(f"Aktualisiere Lieferant ID {lieferant_id}: {name}")
        
        # Prüfen ob Lieferant existiert
        if not self.lieferant_finden(lieferant_id):
            raise NotFoundError(f"Lieferant mit ID {lieferant_id} nicht gefunden")
        
        try:
            query = "UPDATE lieferanten SET name = ?, kontakt = ? WHERE id = ?"
            self.db.execute_query(query, (name, kontakt, lieferant_id))
            app_logger.info(f"Lieferant ID {lieferant_id} erfolgreich aktualisiert")
            return True
        except DatabaseError as e:
            if "UNIQUE constraint failed" in str(e):
                raise LieferantError(f"Lieferant '{name}' existiert bereits")
            raise LieferantError(f"Fehler beim Aktualisieren des Lieferanten: {e}")
    
    def lieferant_loeschen(self, lieferant_id: int) -> bool:
        if lieferant_id <= 0:
            raise ValidationError("Ungültige Lieferanten-ID")
        
        app_logger.info(f"Lösche Lieferant ID {lieferant_id}")
        
        # Prüfen ob Lieferant existiert
        if not self.lieferant_finden(lieferant_id):
            raise NotFoundError(f"Lieferant mit ID {lieferant_id} nicht gefunden")
        
        try:
            # Prüfen ob Artikel mit diesem Lieferanten existieren
            artikel_check = self.db.execute_query(
                "SELECT COUNT(*) FROM artikel WHERE lieferant_id = ?", 
                (lieferant_id,)
            )
            if artikel_check[0][0] > 0:
                raise IntegrityError(f"Lieferant kann nicht gelöscht werden: {artikel_check[0][0]} Artikel sind zugeordnet")
            
            query = "DELETE FROM lieferanten WHERE id = ?"
            self.db.execute_query(query, (lieferant_id,))
            app_logger.info(f"Lieferant ID {lieferant_id} erfolgreich gelöscht")
            return True
        except DatabaseError as e:
            raise LieferantError(f"Fehler beim Löschen des Lieferanten: {e}")
    
    # Artikel Management
    def artikel_hinzufuegen(self, artikelnummer: str, bezeichnung: str, lieferant_id: int, mindestmenge: int = 1) -> bool:
        if not artikelnummer or not artikelnummer.strip():
            raise ValidationError("Artikelnummer darf nicht leer sein")
        if not bezeichnung or not bezeichnung.strip():
            raise ValidationError("Artikelbezeichnung darf nicht leer sein")
        if lieferant_id <= 0:
            raise ValidationError("Ungültige Lieferanten-ID")
        if mindestmenge < 0:
            raise ValidationError("Mindestmenge darf nicht negativ sein")
        
        artikelnummer = artikelnummer.strip()
        bezeichnung = bezeichnung.strip()
        app_logger.info(f"Füge Artikel hinzu: {artikelnummer} - {bezeichnung}")
        
        # Prüfen ob Lieferant existiert
        if not self.lieferant_finden(lieferant_id):
            raise NotFoundError(f"Lieferant mit ID {lieferant_id} nicht gefunden")
        
        try:
            query = "INSERT INTO artikel (artikelnummer, bezeichnung, lieferant_id, mindestmenge) VALUES (?, ?, ?, ?)"
            self.db.execute_insert(query, (artikelnummer, bezeichnung, lieferant_id, mindestmenge))
            app_logger.info(f"Artikel {artikelnummer} erfolgreich hinzugefügt")
            return True
        except DatabaseError as e:
            if "UNIQUE constraint failed" in str(e):
                raise ArtikelError(f"Artikel '{artikelnummer}' existiert bereits")
            raise ArtikelError(f"Fehler beim Hinzufügen des Artikels: {e}")
    
    def artikel_auflisten(self) -> List[tuple]:
        query = """
        SELECT a.artikelnummer, a.bezeichnung, l.name as lieferant_name, a.mindestmenge
        FROM artikel a
        JOIN lieferanten l ON a.lieferant_id = l.id
        ORDER BY a.artikelnummer
        """
        return self.db.execute_query(query)
    
    def artikel_finden(self, artikelnummer: str) -> Optional[Artikel]:
        query = "SELECT artikelnummer, bezeichnung, lieferant_id, mindestmenge FROM artikel WHERE artikelnummer = ?"
        results = self.db.execute_query(query, (artikelnummer,))
        if results:
            row = results[0]
            return Artikel(artikelnummer=row[0], bezeichnung=row[1], lieferant_id=row[2], mindestmenge=row[3])
        return None
    
    # Kunden Management
    def kunde_hinzufuegen(self, name: str, kontakt: str = "") -> int:
        query = "INSERT INTO kunden (name, kontakt) VALUES (?, ?)"
        return self.db.execute_insert(query, (name, kontakt))
    
    def kunden_auflisten(self) -> List[Kunde]:
        query = "SELECT id, name, kontakt FROM kunden ORDER BY name"
        results = self.db.execute_query(query)
        return [Kunde(id=row[0], name=row[1], kontakt=row[2]) for row in results]
    
    def kunde_finden(self, kunde_id: int) -> Optional[Kunde]:
        query = "SELECT id, name, kontakt FROM kunden WHERE id = ?"
        results = self.db.execute_query(query, (kunde_id,))
        if results:
            row = results[0]
            return Kunde(id=row[0], name=row[1], kontakt=row[2])
        return None
    
    # Projekt Management
    def projekt_hinzufuegen(self, projektname: str, kunde_id: int) -> int:
        query = "INSERT INTO projekte (projektname, kunde_id) VALUES (?, ?)"
        return self.db.execute_insert(query, (projektname, kunde_id))
    
    def projekte_auflisten(self) -> List[tuple]:
        query = """
        SELECT p.id, p.projektname, k.name as kunde_name
        FROM projekte p
        JOIN kunden k ON p.kunde_id = k.id
        ORDER BY p.projektname
        """
        return self.db.execute_query(query)
    
    # Lager Management
    def lagereingang(self, artikelnummer: str, menge: int, einkaufspreis: float, 
                    einlagerungsdatum: str = None) -> bool:
        if einlagerungsdatum is None:
            einlagerungsdatum = datetime.now().strftime("%Y-%m-%d")
        
        # Prüfen ob Artikel existiert
        if not self.artikel_finden(artikelnummer):
            return False
        
        query = """
        INSERT INTO lagerbestand (artikelnummer, verfuegbare_menge, einkaufspreis, einlagerungsdatum)
        VALUES (?, ?, ?, ?)
        """
        self.db.execute_insert(query, (artikelnummer, menge, einkaufspreis, einlagerungsdatum))
        return True
    
    def lagerbestand_artikel(self, artikelnummer: str, include_zero: bool = False) -> List[Lagerbestand]:
        if include_zero:
            query = """
            SELECT id, artikelnummer, verfuegbare_menge, einkaufspreis, einlagerungsdatum
            FROM lagerbestand
            WHERE artikelnummer = ?
            ORDER BY einlagerungsdatum
            """
        else:
            query = """
            SELECT id, artikelnummer, verfuegbare_menge, einkaufspreis, einlagerungsdatum
            FROM lagerbestand
            WHERE artikelnummer = ? AND verfuegbare_menge > 0
            ORDER BY einlagerungsdatum
            """
        results = self.db.execute_query(query, (artikelnummer,))
        return [Lagerbestand(id=row[0], artikelnummer=row[1], verfuegbare_menge=row[2], 
                            einkaufspreis=row[3], einlagerungsdatum=row[4]) for row in results]
    
    def gesamter_lagerbestand(self) -> List[tuple]:
        query = """
        SELECT l.artikelnummer, a.bezeichnung, 
               SUM(l.verfuegbare_menge) as gesamtmenge,
               AVG(l.einkaufspreis) as durchschnittspreis
        FROM lagerbestand l
        JOIN artikel a ON l.artikelnummer = a.artikelnummer
        WHERE l.verfuegbare_menge > 0
        GROUP BY l.artikelnummer, a.bezeichnung
        ORDER BY l.artikelnummer
        """
        return self.db.execute_query(query)
    
    def artikel_unter_mindestmenge(self) -> List[tuple]:
        """Gibt alle Artikel zurück, die unter der Mindestmenge sind"""
        query = """
        SELECT a.artikelnummer, a.bezeichnung, a.mindestmenge,
               COALESCE(SUM(l.verfuegbare_menge), 0) as aktueller_bestand,
               l_info.name as lieferant_name
        FROM artikel a
        LEFT JOIN lagerbestand l ON a.artikelnummer = l.artikelnummer AND l.verfuegbare_menge > 0
        JOIN lieferanten l_info ON a.lieferant_id = l_info.id
        GROUP BY a.artikelnummer, a.bezeichnung, a.mindestmenge, l_info.name
        HAVING COALESCE(SUM(l.verfuegbare_menge), 0) < a.mindestmenge
        ORDER BY a.artikelnummer
        """
        return self.db.execute_query(query)
    
    # Verkauf System (FIFO)
    def verkauf(self, projekt_id: int, artikelnummer: str, verkaufte_menge: int, 
               verkaufspreis: float, verkaufsdatum: str = None) -> bool:
        if verkaufsdatum is None:
            verkaufsdatum = datetime.now().strftime("%Y-%m-%d")
        
        # FIFO: Älteste Bestände zuerst verkaufen
        lagerbestaende = self.lagerbestand_artikel(artikelnummer)
        
        # Prüfen ob genug Ware verfügbar ist
        verfuegbare_gesamtmenge = sum(bestand.verfuegbare_menge for bestand in lagerbestaende)
        if verfuegbare_gesamtmenge < verkaufte_menge:
            return False
        
        verbleibende_menge = verkaufte_menge
        
        # FIFO: Von den ältesten Beständen abziehen
        for bestand in lagerbestaende:
            if verbleibende_menge <= 0:
                break
            
            if bestand.verfuegbare_menge >= verbleibende_menge:
                # Komplett aus diesem Bestand verkaufen
                neue_menge = bestand.verfuegbare_menge - verbleibende_menge
                self.db.execute_query(
                    "UPDATE lagerbestand SET verfuegbare_menge = ? WHERE id = ?",
                    (neue_menge, bestand.id)
                )
                verbleibende_menge = 0
            else:
                # Diesen Bestand komplett verkaufen
                verbleibende_menge -= bestand.verfuegbare_menge
                self.db.execute_query(
                    "UPDATE lagerbestand SET verfuegbare_menge = 0 WHERE id = ?",
                    (bestand.id,)
                )
        
        # Verkauf in Verkäufe Tabelle eintragen
        query = """
        INSERT INTO verkaeufe (projekt_id, artikelnummer, verkaufte_menge, verkaufspreis, verkaufsdatum)
        VALUES (?, ?, ?, ?, ?)
        """
        self.db.execute_insert(query, (projekt_id, artikelnummer, verkaufte_menge, verkaufspreis, verkaufsdatum))
        return True
    
    def projekt_verkaeufe(self, projekt_id: int) -> List[tuple]:
        query = """
        SELECT v.artikelnummer, a.bezeichnung, v.verkaufte_menge, v.verkaufspreis, v.verkaufsdatum
        FROM verkaeufe v
        JOIN artikel a ON v.artikelnummer = a.artikelnummer
        WHERE v.projekt_id = ?
        ORDER BY v.verkaufsdatum
        """
        return self.db.execute_query(query, (projekt_id,))