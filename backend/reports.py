from typing import List, Dict
from database import Database
from inventory_manager import InventoryManager

class ReportGenerator:
    def __init__(self):
        self.db = Database()
        self.inventory = InventoryManager()
    
    def lagerbestand_detailliert(self) -> List[Dict]:
        query = """
        SELECT l.id, l.artikelnummer, a.bezeichnung, li.name as lieferant,
               l.verfuegbare_menge, l.einkaufspreis, l.einlagerungsdatum,
               (l.verfuegbare_menge * l.einkaufspreis) as gesamtwert
        FROM lagerbestand l
        JOIN artikel a ON l.artikelnummer = a.artikelnummer
        JOIN lieferanten li ON a.lieferant_id = li.id
        WHERE l.verfuegbare_menge > 0
        ORDER BY l.artikelnummer, l.einlagerungsdatum
        """
        results = self.db.execute_query(query)
        
        berichte = []
        for row in results:
            berichte.append({
                'lager_id': row[0],
                'artikelnummer': row[1],
                'bezeichnung': row[2],
                'lieferant': row[3],
                'menge': row[4],
                'einkaufspreis': row[5],
                'einlagerungsdatum': row[6],
                'gesamtwert': row[7]
            })
        
        return berichte
    
    def lagerbestand_zusammenfassung(self) -> List[Dict]:
        query = """
        SELECT l.artikelnummer, a.bezeichnung, li.name as lieferant,
               SUM(l.verfuegbare_menge) as gesamtmenge,
               AVG(l.einkaufspreis) as durchschnittspreis,
               SUM(l.verfuegbare_menge * l.einkaufspreis) as gesamtwert,
               MIN(l.einlagerungsdatum) as aeltestes_datum,
               MAX(l.einlagerungsdatum) as neuestes_datum
        FROM lagerbestand l
        JOIN artikel a ON l.artikelnummer = a.artikelnummer
        JOIN lieferanten li ON a.lieferant_id = li.id
        WHERE l.verfuegbare_menge > 0
        GROUP BY l.artikelnummer, a.bezeichnung, li.name
        ORDER BY l.artikelnummer
        """
        results = self.db.execute_query(query)
        
        berichte = []
        for row in results:
            berichte.append({
                'artikelnummer': row[0],
                'bezeichnung': row[1],
                'lieferant': row[2],
                'gesamtmenge': row[3],
                'durchschnittspreis': row[4],
                'gesamtwert': row[5],
                'aeltestes_datum': row[6],
                'neuestes_datum': row[7]
            })
        
        return berichte
    
    def projekt_uebersicht(self, projekt_id: int) -> Dict:
        # Projekt-Informationen
        projekt_query = """
        SELECT p.projektname, k.name as kunde_name
        FROM projekte p
        JOIN kunden k ON p.kunde_id = k.id
        WHERE p.id = ?
        """
        projekt_info = self.db.execute_query(projekt_query, (projekt_id,))
        
        if not projekt_info:
            return None
        
        # Verkäufe für dieses Projekt
        verkaeufe_query = """
        SELECT v.artikelnummer, a.bezeichnung, v.verkaufte_menge, 
               v.verkaufspreis, v.verkaufsdatum,
               (v.verkaufte_menge * v.verkaufspreis) as umsatz
        FROM verkaeufe v
        JOIN artikel a ON v.artikelnummer = a.artikelnummer
        WHERE v.projekt_id = ?
        ORDER BY v.verkaufsdatum, v.artikelnummer
        """
        verkaeufe = self.db.execute_query(verkaeufe_query, (projekt_id,))
        
        verkauf_details = []
        gesamtumsatz = 0
        
        for verkauf in verkaeufe:
            detail = {
                'artikelnummer': verkauf[0],
                'bezeichnung': verkauf[1],
                'menge': verkauf[2],
                'verkaufspreis': verkauf[3],
                'verkaufsdatum': verkauf[4],
                'umsatz': verkauf[5]
            }
            verkauf_details.append(detail)
            gesamtumsatz += verkauf[5]
        
        return {
            'projektname': projekt_info[0][0],
            'kunde': projekt_info[0][1],
            'verkaeufe': verkauf_details,
            'gesamtumsatz': gesamtumsatz
        }
    
    def alle_projekte_uebersicht(self) -> List[Dict]:
        query = """
        SELECT p.id, p.projektname, k.name as kunde_name,
               COUNT(v.id) as anzahl_verkaeufe,
               COALESCE(SUM(v.verkaufte_menge * v.verkaufspreis), 0) as gesamtumsatz
        FROM projekte p
        JOIN kunden k ON p.kunde_id = k.id
        LEFT JOIN verkaeufe v ON p.id = v.projekt_id
        GROUP BY p.id, p.projektname, k.name
        ORDER BY p.projektname
        """
        results = self.db.execute_query(query)
        
        projekte = []
        for row in results:
            projekte.append({
                'projekt_id': row[0],
                'projektname': row[1],
                'kunde': row[2],
                'anzahl_verkaeufe': row[3],
                'gesamtumsatz': row[4]
            })
        
        return projekte
    
    def gewinn_analyse(self, projekt_id: int = None) -> Dict:
        if projekt_id:
            # Analyse für ein spezifisches Projekt
            where_clause = "WHERE v.projekt_id = ?"
            params = (projekt_id,)
        else:
            # Analyse für alle Projekte
            where_clause = ""
            params = ()
        
        query = f"""
        SELECT v.artikelnummer, a.bezeichnung,
               SUM(v.verkaufte_menge) as gesamt_verkauft,
               AVG(v.verkaufspreis) as durchschnitt_verkaufspreis,
               SUM(v.verkaufte_menge * v.verkaufspreis) as gesamtumsatz
        FROM verkaeufe v
        JOIN artikel a ON v.artikelnummer = a.artikelnummer
        {where_clause}
        GROUP BY v.artikelnummer, a.bezeichnung
        ORDER BY gesamtumsatz DESC
        """
        
        verkaeufe = self.db.execute_query(query, params)
        
        analyse = []
        gesamtumsatz = 0
        
        for verkauf in verkaeufe:
            artikelnummer = verkauf[0]
            
            # Durchschnittlichen Einkaufspreis für verkaufte Mengen berechnen
            einkauf_query = """
            SELECT AVG(einkaufspreis) as durchschnitt_einkauf
            FROM lagerbestand
            WHERE artikelnummer = ?
            """
            einkauf_result = self.db.execute_query(einkauf_query, (artikelnummer,))
            durchschnitt_einkauf = einkauf_result[0][0] if einkauf_result[0][0] else 0
            
            umsatz = verkauf[4]
            kosten = verkauf[2] * durchschnitt_einkauf
            gewinn = umsatz - kosten
            
            analyse.append({
                'artikelnummer': verkauf[0],
                'bezeichnung': verkauf[1],
                'verkaufte_menge': verkauf[2],
                'durchschnitt_verkaufspreis': verkauf[3],
                'durchschnitt_einkaufspreis': durchschnitt_einkauf,
                'umsatz': umsatz,
                'kosten': kosten,
                'gewinn': gewinn,
                'gewinnmarge': (gewinn / umsatz * 100) if umsatz > 0 else 0
            })
            
            gesamtumsatz += umsatz
        
        gesamtkosten = sum(item['kosten'] for item in analyse)
        gesamtgewinn = gesamtumsatz - gesamtkosten
        
        return {
            'artikel_analyse': analyse,
            'gesamtumsatz': gesamtumsatz,
            'gesamtkosten': gesamtkosten,
            'gesamtgewinn': gesamtgewinn,
            'gesamtgewinnmarge': (gesamtgewinn / gesamtumsatz * 100) if gesamtumsatz > 0 else 0
        }
    
    def lagerumschlag(self) -> List[Dict]:
        query = """
        SELECT a.artikelnummer, a.bezeichnung,
               COALESCE(SUM(l.verfuegbare_menge), 0) as lagerbestand,
               COALESCE(SUM(v.verkaufte_menge), 0) as verkaufte_menge,
               COUNT(DISTINCT v.id) as anzahl_verkaeufe
        FROM artikel a
        LEFT JOIN lagerbestand l ON a.artikelnummer = l.artikelnummer AND l.verfuegbare_menge > 0
        LEFT JOIN verkaeufe v ON a.artikelnummer = v.artikelnummer
        GROUP BY a.artikelnummer, a.bezeichnung
        ORDER BY verkaufte_menge DESC
        """
        results = self.db.execute_query(query)
        
        umschlag = []
        for row in results:
            lagerbestand = row[2]
            verkaufte_menge = row[3]
            
            if lagerbestand > 0 and verkaufte_menge > 0:
                umschlagrate = verkaufte_menge / lagerbestand
            else:
                umschlagrate = 0
            
            umschlag.append({
                'artikelnummer': row[0],
                'bezeichnung': row[1],
                'lagerbestand': lagerbestand,
                'verkaufte_menge': verkaufte_menge,
                'anzahl_verkaeufe': row[4],
                'umschlagrate': umschlagrate
            })
        
        return umschlag