#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from datetime import datetime
from inventory_manager import InventoryManager
from reports import ReportGenerator

class LagerverwaltungCLI:
    def __init__(self):
        self.inventory = InventoryManager()
        self.reports = ReportGenerator()
    
    def hauptmenu(self):
        while True:
            print("\n" + "="*50)
            print("    LAGERVERWALTUNG EINRICHTUNGSHAUS")
            print("="*50)
            print("1. Lieferanten verwalten")
            print("2. Artikel verwalten") 
            print("3. Kunden verwalten")
            print("4. Projekte verwalten")
            print("5. Lagereingang")
            print("6. Verkauf")
            print("7. Berichte")
            print("0. Programm beenden")
            print("-"*50)
            
            wahl = input("Ihre Wahl: ").strip()
            
            if wahl == "1":
                self.lieferanten_menu()
            elif wahl == "2":
                self.artikel_menu()
            elif wahl == "3":
                self.kunden_menu()
            elif wahl == "4":
                self.projekte_menu()
            elif wahl == "5":
                self.lagereingang_menu()
            elif wahl == "6":
                self.verkauf_menu()
            elif wahl == "7":
                self.berichte_menu()
            elif wahl == "0":
                print("Auf Wiedersehen!")
                sys.exit()
            else:
                print("Ungültige Eingabe!")
    
    def lieferanten_menu(self):
        while True:
            print("\n--- LIEFERANTEN VERWALTEN ---")
            print("1. Lieferant hinzufügen")
            print("2. Alle Lieferanten anzeigen")
            print("0. Zurück zum Hauptmenü")
            
            wahl = input("Ihre Wahl: ").strip()
            
            if wahl == "1":
                name = input("Lieferantenname: ").strip()
                kontakt = input("Kontakt (optional): ").strip()
                
                if name:
                    lieferant_id = self.inventory.lieferant_hinzufuegen(name, kontakt)
                    print(f"Lieferant '{name}' wurde hinzugefügt (ID: {lieferant_id})")
                else:
                    print("Name darf nicht leer sein!")
            
            elif wahl == "2":
                lieferanten = self.inventory.lieferanten_auflisten()
                if lieferanten:
                    print(f"\n{'ID':<5} {'Name':<30} {'Kontakt'}")
                    print("-" * 60)
                    for l in lieferanten:
                        print(f"{l.id:<5} {l.name:<30} {l.kontakt}")
                else:
                    print("Keine Lieferanten vorhanden.")
            
            elif wahl == "0":
                break
            else:
                print("Ungültige Eingabe!")
    
    def artikel_menu(self):
        while True:
            print("\n--- ARTIKEL VERWALTEN ---")
            print("1. Artikel hinzufügen")
            print("2. Alle Artikel anzeigen")
            print("0. Zurück zum Hauptmenü")
            
            wahl = input("Ihre Wahl: ").strip()
            
            if wahl == "1":
                # Lieferanten anzeigen
                lieferanten = self.inventory.lieferanten_auflisten()
                if not lieferanten:
                    print("Bitte erst einen Lieferanten anlegen!")
                    continue
                
                print("\nVerfügbare Lieferanten:")
                for l in lieferanten:
                    print(f"{l.id}: {l.name}")
                
                try:
                    lieferant_id = int(input("Lieferanten-ID: "))
                    artikelnummer = input("Artikelnummer: ").strip()
                    bezeichnung = input("Bezeichnung: ").strip()
                    
                    if artikelnummer and bezeichnung:
                        if self.inventory.artikel_hinzufuegen(artikelnummer, bezeichnung, lieferant_id):
                            print(f"Artikel '{artikelnummer}' wurde hinzugefügt")
                        else:
                            print("Fehler beim Hinzufügen (Artikelnummer bereits vorhanden?)")
                    else:
                        print("Artikelnummer und Bezeichnung dürfen nicht leer sein!")
                except ValueError:
                    print("Ungültige Lieferanten-ID!")
            
            elif wahl == "2":
                artikel = self.inventory.artikel_auflisten()
                if artikel:
                    print(f"\n{'Artikelnummer':<15} {'Bezeichnung':<40} {'Lieferant'}")
                    print("-" * 80)
                    for a in artikel:
                        print(f"{a[0]:<15} {a[1]:<40} {a[2]}")
                else:
                    print("Keine Artikel vorhanden.")
            
            elif wahl == "0":
                break
            else:
                print("Ungültige Eingabe!")
    
    def kunden_menu(self):
        while True:
            print("\n--- KUNDEN VERWALTEN ---")
            print("1. Kunde hinzufügen")
            print("2. Alle Kunden anzeigen")
            print("0. Zurück zum Hauptmenü")
            
            wahl = input("Ihre Wahl: ").strip()
            
            if wahl == "1":
                name = input("Kundenname: ").strip()
                kontakt = input("Kontakt (optional): ").strip()
                
                if name:
                    kunde_id = self.inventory.kunde_hinzufuegen(name, kontakt)
                    print(f"Kunde '{name}' wurde hinzugefügt (ID: {kunde_id})")
                else:
                    print("Name darf nicht leer sein!")
            
            elif wahl == "2":
                kunden = self.inventory.kunden_auflisten()
                if kunden:
                    print(f"\n{'ID':<5} {'Name':<30} {'Kontakt'}")
                    print("-" * 60)
                    for k in kunden:
                        print(f"{k.id:<5} {k.name:<30} {k.kontakt}")
                else:
                    print("Keine Kunden vorhanden.")
            
            elif wahl == "0":
                break
            else:
                print("Ungültige Eingabe!")
    
    def projekte_menu(self):
        while True:
            print("\n--- PROJEKTE VERWALTEN ---")
            print("1. Projekt hinzufügen")
            print("2. Alle Projekte anzeigen")
            print("0. Zurück zum Hauptmenü")
            
            wahl = input("Ihre Wahl: ").strip()
            
            if wahl == "1":
                kunden = self.inventory.kunden_auflisten()
                if not kunden:
                    print("Bitte erst einen Kunden anlegen!")
                    continue
                
                print("\nVerfügbare Kunden:")
                for k in kunden:
                    print(f"{k.id}: {k.name}")
                
                try:
                    kunde_id = int(input("Kunden-ID: "))
                    projektname = input("Projektname: ").strip()
                    
                    if projektname:
                        projekt_id = self.inventory.projekt_hinzufuegen(projektname, kunde_id)
                        print(f"Projekt '{projektname}' wurde hinzugefügt (ID: {projekt_id})")
                    else:
                        print("Projektname darf nicht leer sein!")
                except ValueError:
                    print("Ungültige Kunden-ID!")
            
            elif wahl == "2":
                projekte = self.inventory.projekte_auflisten()
                if projekte:
                    print(f"\n{'ID':<5} {'Projektname':<30} {'Kunde'}")
                    print("-" * 60)
                    for p in projekte:
                        print(f"{p[0]:<5} {p[1]:<30} {p[2]}")
                else:
                    print("Keine Projekte vorhanden.")
            
            elif wahl == "0":
                break
            else:
                print("Ungültige Eingabe!")
    
    def lagereingang_menu(self):
        print("\n--- LAGEREINGANG ---")
        
        artikel = self.inventory.artikel_auflisten()
        if not artikel:
            print("Bitte erst Artikel anlegen!")
            return
        
        print("\nVerfügbare Artikel:")
        for a in artikel:
            print(f"{a[0]}: {a[1]} (Lieferant: {a[2]})")
        
        try:
            artikelnummer = input("Artikelnummer: ").strip()
            menge = int(input("Menge: "))
            einkaufspreis = float(input("Einkaufspreis (netto): "))
            datum = input("Einlagerungsdatum (YYYY-MM-DD, Enter für heute): ").strip()
            
            if not datum:
                datum = datetime.now().strftime("%Y-%m-%d")
            
            if self.inventory.lagereingang(artikelnummer, menge, einkaufspreis, datum):
                print(f"Lagereingang erfolgreich: {menge} x {artikelnummer} zu {einkaufspreis}€")
            else:
                print("Fehler: Artikel nicht gefunden!")
        except ValueError:
            print("Ungültige Eingabe für Menge oder Preis!")
    
    def verkauf_menu(self):
        print("\n--- VERKAUF ---")
        
        # Projekte anzeigen
        projekte = self.inventory.projekte_auflisten()
        if not projekte:
            print("Bitte erst ein Projekt anlegen!")
            return
        
        print("\nVerfügbare Projekte:")
        for p in projekte:
            print(f"{p[0]}: {p[1]} (Kunde: {p[2]})")
        
        # Verfügbare Artikel im Lager anzeigen
        lagerbestand = self.inventory.gesamter_lagerbestand()
        if not lagerbestand:
            print("Keine Artikel im Lager verfügbar!")
            return
        
        print("\nVerfügbare Artikel im Lager:")
        for l in lagerbestand:
            print(f"{l[0]}: {l[1]} - Verfügbar: {l[2]} Stück")
        
        try:
            projekt_id = int(input("Projekt-ID: "))
            artikelnummer = input("Artikelnummer: ").strip()
            menge = int(input("Verkaufte Menge: "))
            verkaufspreis = float(input("Verkaufspreis pro Stück (netto): "))
            datum = input("Verkaufsdatum (YYYY-MM-DD, Enter für heute): ").strip()
            
            if not datum:
                datum = datetime.now().strftime("%Y-%m-%d")
            
            if self.inventory.verkauf(projekt_id, artikelnummer, menge, verkaufspreis, datum):
                print(f"Verkauf erfolgreich: {menge} x {artikelnummer} zu {verkaufspreis}€/Stück")
            else:
                print("Fehler: Nicht genügend Artikel im Lager verfügbar!")
        except ValueError:
            print("Ungültige Eingabe!")
    
    def berichte_menu(self):
        while True:
            print("\n--- BERICHTE ---")
            print("1. Lagerbestand detailliert")
            print("2. Lagerbestand Zusammenfassung")
            print("3. Projekt-Übersicht")
            print("4. Alle Projekte")
            print("5. Gewinn-Analyse")
            print("6. Lagerumschlag")
            print("0. Zurück zum Hauptmenü")
            
            wahl = input("Ihre Wahl: ").strip()
            
            if wahl == "1":
                self.zeige_lagerbestand_detailliert()
            elif wahl == "2":
                self.zeige_lagerbestand_zusammenfassung()
            elif wahl == "3":
                self.zeige_projekt_uebersicht()
            elif wahl == "4":
                self.zeige_alle_projekte()
            elif wahl == "5":
                self.zeige_gewinn_analyse()
            elif wahl == "6":
                self.zeige_lagerumschlag()
            elif wahl == "0":
                break
            else:
                print("Ungültige Eingabe!")
    
    def zeige_lagerbestand_detailliert(self):
        bestand = self.reports.lagerbestand_detailliert()
        if bestand:
            print(f"\n{'Art.Nr.':<10} {'Bezeichnung':<25} {'Lieferant':<15} {'Menge':<6} {'Einkauf':<8} {'Datum':<12} {'Wert':<8}")
            print("-" * 95)
            gesamtwert = 0
            for b in bestand:
                print(f"{b['artikelnummer']:<10} {b['bezeichnung']:<25} {b['lieferant']:<15} "
                     f"{b['menge']:<6} {b['einkaufspreis']:<8.2f} {b['einlagerungsdatum']:<12} {b['gesamtwert']:<8.2f}")
                gesamtwert += b['gesamtwert']
            print("-" * 95)
            print(f"Gesamtwert Lager: {gesamtwert:.2f}€")
        else:
            print("Kein Lagerbestand vorhanden.")
    
    def zeige_lagerbestand_zusammenfassung(self):
        bestand = self.reports.lagerbestand_zusammenfassung()
        if bestand:
            print(f"\n{'Art.Nr.':<10} {'Bezeichnung':<25} {'Lieferant':<15} {'Gesamt':<6} {'Ø Preis':<8} {'Wert':<8}")
            print("-" * 85)
            gesamtwert = 0
            for b in bestand:
                print(f"{b['artikelnummer']:<10} {b['bezeichnung']:<25} {b['lieferant']:<15} "
                     f"{b['gesamtmenge']:<6} {b['durchschnittspreis']:<8.2f} {b['gesamtwert']:<8.2f}")
                gesamtwert += b['gesamtwert']
            print("-" * 85)
            print(f"Gesamtwert Lager: {gesamtwert:.2f}€")
        else:
            print("Kein Lagerbestand vorhanden.")
    
    def zeige_projekt_uebersicht(self):
        projekte = self.inventory.projekte_auflisten()
        if not projekte:
            print("Keine Projekte vorhanden!")
            return
        
        print("\nVerfügbare Projekte:")
        for p in projekte:
            print(f"{p[0]}: {p[1]} (Kunde: {p[2]})")
        
        try:
            projekt_id = int(input("Projekt-ID für Detailansicht: "))
            uebersicht = self.reports.projekt_uebersicht(projekt_id)
            
            if uebersicht:
                print(f"\n--- PROJEKT: {uebersicht['projektname']} ---")
                print(f"Kunde: {uebersicht['kunde']}")
                print(f"Gesamtumsatz: {uebersicht['gesamtumsatz']:.2f}€")
                print("\nVerkäufe:")
                print(f"{'Art.Nr.':<10} {'Bezeichnung':<25} {'Menge':<6} {'Preis':<8} {'Datum':<12} {'Umsatz':<8}")
                print("-" * 85)
                for v in uebersicht['verkaeufe']:
                    print(f"{v['artikelnummer']:<10} {v['bezeichnung']:<25} {v['menge']:<6} "
                         f"{v['verkaufspreis']:<8.2f} {v['verkaufsdatum']:<12} {v['umsatz']:<8.2f}")
            else:
                print("Projekt nicht gefunden!")
        except ValueError:
            print("Ungültige Projekt-ID!")
    
    def zeige_alle_projekte(self):
        projekte = self.reports.alle_projekte_uebersicht()
        if projekte:
            print(f"\n{'ID':<5} {'Projektname':<25} {'Kunde':<20} {'Verkäufe':<9} {'Umsatz':<10}")
            print("-" * 75)
            for p in projekte:
                print(f"{p['projekt_id']:<5} {p['projektname']:<25} {p['kunde']:<20} "
                     f"{p['anzahl_verkaeufe']:<9} {p['gesamtumsatz']:<10.2f}")
        else:
            print("Keine Projekte vorhanden.")
    
    def zeige_gewinn_analyse(self):
        print("\n1. Alle Projekte")
        print("2. Spezifisches Projekt")
        wahl = input("Ihre Wahl: ").strip()
        
        projekt_id = None
        if wahl == "2":
            projekte = self.inventory.projekte_auflisten()
            if not projekte:
                print("Keine Projekte vorhanden!")
                return
            
            print("\nVerfügbare Projekte:")
            for p in projekte:
                print(f"{p[0]}: {p[1]} (Kunde: {p[2]})")
            
            try:
                projekt_id = int(input("Projekt-ID: "))
            except ValueError:
                print("Ungültige Projekt-ID!")
                return
        
        analyse = self.reports.gewinn_analyse(projekt_id)
        
        print(f"\n{'Art.Nr.':<10} {'Bezeichnung':<20} {'Verkauft':<8} {'VK-Preis':<8} {'EK-Preis':<8} {'Umsatz':<8} {'Gewinn':<8} {'Marge %':<8}")
        print("-" * 90)
        
        for a in analyse['artikel_analyse']:
            print(f"{a['artikelnummer']:<10} {a['bezeichnung']:<20} {a['verkaufte_menge']:<8} "
                 f"{a['durchschnitt_verkaufspreis']:<8.2f} {a['durchschnitt_einkaufspreis']:<8.2f} "
                 f"{a['umsatz']:<8.2f} {a['gewinn']:<8.2f} {a['gewinnmarge']:<8.1f}")
        
        print("-" * 90)
        print(f"GESAMT: Umsatz: {analyse['gesamtumsatz']:.2f}€, "
             f"Kosten: {analyse['gesamtkosten']:.2f}€, "
             f"Gewinn: {analyse['gesamtgewinn']:.2f}€, "
             f"Marge: {analyse['gesamtgewinnmarge']:.1f}%")
    
    def zeige_lagerumschlag(self):
        umschlag = self.reports.lagerumschlag()
        if umschlag:
            print(f"\n{'Art.Nr.':<10} {'Bezeichnung':<25} {'Lager':<6} {'Verkauft':<8} {'Verkäufe':<9} {'Umschlag':<8}")
            print("-" * 80)
            for u in umschlag:
                print(f"{u['artikelnummer']:<10} {u['bezeichnung']:<25} {u['lagerbestand']:<6} "
                     f"{u['verkaufte_menge']:<8} {u['anzahl_verkaeufe']:<9} {u['umschlagrate']:<8.2f}")
        else:
            print("Keine Daten verfügbar.")

def main():
    try:
        app = LagerverwaltungCLI()
        app.hauptmenu()
    except KeyboardInterrupt:
        print("\n\nProgramm beendet.")
    except Exception as e:
        print(f"Fehler: {e}")

if __name__ == "__main__":
    main()