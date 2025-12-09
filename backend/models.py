from datetime import datetime
from typing import List, Optional

class Lieferant:
    def __init__(self, id: int = None, name: str = "", kontakt: str = ""):
        self.id = id
        self.name = name
        self.kontakt = kontakt

class Artikel:
    def __init__(self, artikelnummer: str = "", bezeichnung: str = "", lieferant_id: int = None, mindestmenge: int = 1):
        self.artikelnummer = artikelnummer
        self.bezeichnung = bezeichnung
        self.lieferant_id = lieferant_id
        self.mindestmenge = mindestmenge

class Kunde:
    def __init__(self, id: int = None, name: str = "", kontakt: str = ""):
        self.id = id
        self.name = name
        self.kontakt = kontakt

class Projekt:
    def __init__(self, id: int = None, projektname: str = "", kunde_id: int = None):
        self.id = id
        self.projektname = projektname
        self.kunde_id = kunde_id

class Lagerbestand:
    def __init__(self, id: int = None, artikelnummer: str = "", verfuegbare_menge: int = 0, 
                 einkaufspreis: float = 0.0, einlagerungsdatum: str = ""):
        self.id = id
        self.artikelnummer = artikelnummer
        self.verfuegbare_menge = verfuegbare_menge
        self.einkaufspreis = einkaufspreis
        self.einlagerungsdatum = einlagerungsdatum

class Verkauf:
    def __init__(self, id: int = None, projekt_id: int = None, artikelnummer: str = "", 
                 verkaufte_menge: int = 0, verkaufspreis: float = 0.0, verkaufsdatum: str = ""):
        self.id = id
        self.projekt_id = projekt_id
        self.artikelnummer = artikelnummer
        self.verkaufte_menge = verkaufte_menge
        self.verkaufspreis = verkaufspreis
        self.verkaufsdatum = verkaufsdatum