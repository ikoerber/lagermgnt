import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_path="lagerverwaltung.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
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
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor.fetchall()
    
    def execute_insert(self, query, params):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid