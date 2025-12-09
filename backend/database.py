import sqlite3
import os
from datetime import datetime
from logger_config import app_logger
from exceptions import DatabaseError

class Database:
    def __init__(self, db_path="lagerverwaltung.db"):
        self.db_path = db_path
        app_logger.info(f"Initialisiere Datenbank: {db_path}")
        try:
            self.init_database()
            app_logger.info("Datenbank erfolgreich initialisiert")
        except Exception as e:
            app_logger.error(f"Fehler bei Datenbank-Initialisierung: {e}")
            raise DatabaseError(f"Datenbank-Initialisierung fehlgeschlagen: {e}")
    
    def get_connection(self):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA foreign_keys = ON")
            return conn
        except sqlite3.Error as e:
            app_logger.error(f"Datenbankverbindung fehlgeschlagen: {e}")
            raise DatabaseError(f"Datenbankverbindung fehlgeschlagen: {e}")
    
    def init_database(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Lieferanten Tabelle
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS lieferanten (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    kontakt TEXT
                )
            ''')
            
            # Artikel Tabelle
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS artikel (
                    artikelnummer TEXT PRIMARY KEY,
                    bezeichnung TEXT NOT NULL,
                    lieferant_id INTEGER NOT NULL,
                    mindestmenge INTEGER DEFAULT 1,
                    FOREIGN KEY (lieferant_id) REFERENCES lieferanten (id)
                )
            ''')
            
            # Migration: Spalte mindestmenge hinzufügen falls sie noch nicht existiert
            cursor.execute("PRAGMA table_info(artikel)")
            columns = [column[1] for column in cursor.fetchall()]
            if 'mindestmenge' not in columns:
                cursor.execute("ALTER TABLE artikel ADD COLUMN mindestmenge INTEGER DEFAULT 1")
            
            # Kunden Tabelle
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS kunden (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    kontakt TEXT
                )
            ''')
            
            # Projekte Tabelle
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS projekte (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    projektname TEXT NOT NULL UNIQUE,
                    kunde_id INTEGER NOT NULL,
                    FOREIGN KEY (kunde_id) REFERENCES kunden (id)
                )
            ''')
            
            # Lagerbestand Tabelle
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS lagerbestand (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    artikelnummer TEXT NOT NULL,
                    verfuegbare_menge INTEGER NOT NULL,
                    einkaufspreis REAL NOT NULL,
                    einlagerungsdatum TEXT NOT NULL,
                    FOREIGN KEY (artikelnummer) REFERENCES artikel (artikelnummer)
                )
            ''')
            
            # Verkäufe Tabelle
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS verkaeufe (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    projekt_id INTEGER NOT NULL,
                    artikelnummer TEXT NOT NULL,
                    verkaufte_menge INTEGER NOT NULL,
                    verkaufspreis REAL NOT NULL,
                    verkaufsdatum TEXT NOT NULL,
                    FOREIGN KEY (projekt_id) REFERENCES projekte (id),
                    FOREIGN KEY (artikelnummer) REFERENCES artikel (artikelnummer)
                )
            ''')
            
            conn.commit()
    
    def execute_query(self, query, params=None):
        try:
            app_logger.debug(f"Führe Query aus: {query[:100]}..." + ("" if len(query) <= 100 else ""))
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                conn.commit()
                result = cursor.fetchall()
                app_logger.debug(f"Query erfolgreich, {len(result)} Zeilen zurückgegeben")
                return result
        except sqlite3.IntegrityError as e:
            app_logger.error(f"Integritätsfehler bei Query: {e}")
            raise DatabaseError(f"Integritätsfehler: {e}")
        except sqlite3.Error as e:
            app_logger.error(f"SQL-Fehler bei Query: {e}")
            raise DatabaseError(f"Datenbankfehler: {e}")
        except Exception as e:
            app_logger.error(f"Unerwarteter Fehler bei Query: {e}")
            raise DatabaseError(f"Unerwarteter Datenbankfehler: {e}")
    
    def execute_insert(self, query, params):
        try:
            app_logger.debug(f"Führe Insert aus: {query[:100]}..." + ("" if len(query) <= 100 else ""))
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                lastrowid = cursor.lastrowid
                app_logger.debug(f"Insert erfolgreich, ID: {lastrowid}")
                return lastrowid
        except sqlite3.IntegrityError as e:
            app_logger.error(f"Integritätsfehler bei Insert: {e}")
            raise DatabaseError(f"Integritätsfehler: {e}")
        except sqlite3.Error as e:
            app_logger.error(f"SQL-Fehler bei Insert: {e}")
            raise DatabaseError(f"Datenbankfehler: {e}")
        except Exception as e:
            app_logger.error(f"Unerwarteter Fehler bei Insert: {e}")
            raise DatabaseError(f"Unerwarteter Datenbankfehler: {e}")