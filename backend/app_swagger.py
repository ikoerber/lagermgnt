#!/usr/bin/env python3
"""
Lagerverwaltung Backend API mit Swagger UI
Vollständige REST-API für ein Einrichtungshaus-Lagerverwaltungssystem
"""

from flask import Flask, request
from flask_restx import Api, Resource, fields, Namespace
from flask_cors import CORS
from datetime import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from inventory_manager import InventoryManager
from reports import ReportGenerator

# Flask App Setup
app = Flask(__name__)
CORS(app)

# Swagger API Setup
api = Api(
    app,
    version='1.0',
    title='Lagerverwaltung API',
    description='REST API für Einrichtungshaus-Lagerverwaltung mit FIFO-Prinzip und Mindestmengen-Überwachung',
    doc='/swagger/',
    contact_email='info@lagerverwaltung.de'
)

# Business Logic
inventory = InventoryManager()
reports = ReportGenerator()

# Namespaces
lieferanten_ns = Namespace('lieferanten', description='Lieferanten-Management')
artikel_ns = Namespace('artikel', description='Artikel-Management mit Mindestmengen')
kunden_ns = Namespace('kunden', description='Kunden-Management')
projekte_ns = Namespace('projekte', description='Projekt-Management')
lager_ns = Namespace('lager', description='Lagerbestand und Wareneingänge (FIFO)')
verkauf_ns = Namespace('verkauf', description='Verkaufs-Management (FIFO)')
berichte_ns = Namespace('berichte', description='Berichte und Analysen')

api.add_namespace(lieferanten_ns, path='/api/lieferanten')
api.add_namespace(artikel_ns, path='/api/artikel')
api.add_namespace(kunden_ns, path='/api/kunden')
api.add_namespace(projekte_ns, path='/api/projekte')
api.add_namespace(lager_ns, path='/api/lager')
api.add_namespace(verkauf_ns, path='/api/verkauf')
api.add_namespace(berichte_ns, path='/api/berichte')

# Models für Request/Response Bodies
lieferant_model = api.model('Lieferant', {
    'id': fields.Integer(description='Eindeutige Lieferanten-ID'),
    'name': fields.String(required=True, description='Lieferantenname'),
    'kontakt': fields.String(description='Kontaktinformationen')
})

lieferant_input = api.model('LieferantInput', {
    'name': fields.String(required=True, description='Lieferantenname'),
    'kontakt': fields.String(description='Kontaktinformationen')
})

artikel_model = api.model('Artikel', {
    'artikelnummer': fields.String(description='Eindeutige Artikelnummer'),
    'bezeichnung': fields.String(description='Artikelbezeichnung'),
    'lieferant_name': fields.String(description='Name des Lieferanten'),
    'mindestmenge': fields.Integer(description='Mindestmenge im Lager')
})

artikel_input = api.model('ArtikelInput', {
    'artikelnummer': fields.String(required=True, description='Eindeutige Artikelnummer'),
    'bezeichnung': fields.String(required=True, description='Artikelbezeichnung'),
    'lieferant_id': fields.Integer(required=True, description='ID des Lieferanten'),
    'mindestmenge': fields.Integer(default=1, description='Mindestmenge im Lager')
})

kunde_model = api.model('Kunde', {
    'id': fields.Integer(description='Eindeutige Kunden-ID'),
    'name': fields.String(description='Kundenname'),
    'kontakt': fields.String(description='Kontaktinformationen')
})

kunde_input = api.model('KundeInput', {
    'name': fields.String(required=True, description='Kundenname'),
    'kontakt': fields.String(description='Kontaktinformationen')
})

projekt_model = api.model('Projekt', {
    'id': fields.Integer(description='Eindeutige Projekt-ID'),
    'projektname': fields.String(description='Projektname'),
    'kunde_name': fields.String(description='Name des Kunden')
})

projekt_input = api.model('ProjektInput', {
    'projektname': fields.String(required=True, description='Projektname'),
    'kunde_id': fields.Integer(required=True, description='ID des Kunden')
})

lagereingang_input = api.model('LagereingangInput', {
    'artikelnummer': fields.String(required=True, description='Artikelnummer'),
    'menge': fields.Integer(required=True, description='Eingangsmenge'),
    'einkaufspreis': fields.Float(required=True, description='Einkaufspreis pro Stück (netto)'),
    'einlagerungsdatum': fields.String(description='Einlagerungsdatum (YYYY-MM-DD)')
})

lagerbestand_model = api.model('Lagerbestand', {
    'artikelnummer': fields.String(description='Artikelnummer'),
    'bezeichnung': fields.String(description='Artikelbezeichnung'),
    'gesamtmenge': fields.Integer(description='Gesamtmenge im Lager'),
    'durchschnittspreis': fields.Float(description='Durchschnittlicher Einkaufspreis')
})

verkauf_input = api.model('VerkaufInput', {
    'projekt_id': fields.Integer(required=True, description='ID des Projekts'),
    'artikelnummer': fields.String(required=True, description='Artikelnummer'),
    'verkaufte_menge': fields.Integer(required=True, description='Verkaufte Menge'),
    'verkaufspreis': fields.Float(required=True, description='Verkaufspreis pro Stück (netto)'),
    'verkaufsdatum': fields.String(description='Verkaufsdatum (YYYY-MM-DD)')
})

mindestmenge_model = api.model('MindestmengenBericht', {
    'artikelnummer': fields.String(description='Artikelnummer'),
    'bezeichnung': fields.String(description='Artikelbezeichnung'),
    'mindestmenge': fields.Integer(description='Definierte Mindestmenge'),
    'aktueller_bestand': fields.Integer(description='Aktueller Lagerbestand'),
    'lieferant_name': fields.String(description='Name des Lieferanten'),
    'nachbestellmenge': fields.Integer(description='Empfohlene Nachbestellmenge')
})

error_model = api.model('Error', {
    'error': fields.String(description='Fehlermeldung')
})

# LIEFERANTEN ENDPOINTS
@lieferanten_ns.route('')
class LieferantenList(Resource):
    @lieferanten_ns.marshal_list_with(lieferant_model)
    @lieferanten_ns.doc('list_lieferanten')
    def get(self):
        """Alle Lieferanten auflisten"""
        try:
            lieferanten = inventory.lieferanten_auflisten()
            return [{'id': l.id, 'name': l.name, 'kontakt': l.kontakt} for l in lieferanten]
        except Exception as e:
            api.abort(500, str(e))

    @lieferanten_ns.expect(lieferant_input)
    @lieferanten_ns.marshal_with(lieferant_model, code=201)
    @lieferanten_ns.doc('create_lieferant')
    def post(self):
        """Neuen Lieferanten anlegen"""
        try:
            data = request.get_json()
            if not data or 'name' not in data:
                api.abort(400, 'Name ist erforderlich')
            
            lieferant_id = inventory.lieferant_hinzufuegen(
                data['name'], 
                data.get('kontakt', '')
            )
            return {
                'id': lieferant_id,
                'name': data['name'],
                'kontakt': data.get('kontakt', '')
            }, 201
        except Exception as e:
            api.abort(500, str(e))

@lieferanten_ns.route('/<int:lieferant_id>')
class LieferantDetail(Resource):
    @lieferanten_ns.marshal_with(lieferant_model)
    @lieferanten_ns.doc('get_lieferant')
    def get(self, lieferant_id):
        """Lieferanten-Details abrufen"""
        try:
            lieferant = inventory.lieferant_finden(lieferant_id)
            if not lieferant:
                api.abort(404, 'Lieferant nicht gefunden')
            return {'id': lieferant.id, 'name': lieferant.name, 'kontakt': lieferant.kontakt}
        except Exception as e:
            api.abort(500, str(e))

    @lieferanten_ns.expect(lieferant_input)
    @lieferanten_ns.marshal_with(lieferant_model)
    @lieferanten_ns.doc('update_lieferant')
    def put(self, lieferant_id):
        """Lieferanten aktualisieren"""
        try:
            data = request.get_json()
            if not data or 'name' not in data:
                api.abort(400, 'Name ist erforderlich')
            
            lieferant = inventory.lieferant_finden(lieferant_id)
            if not lieferant:
                api.abort(404, 'Lieferant nicht gefunden')
            
            success = inventory.lieferant_aktualisieren(
                lieferant_id, data['name'], data.get('kontakt', '')
            )
            
            if not success:
                api.abort(400, 'Lieferant konnte nicht aktualisiert werden')
            
            return {'id': lieferant_id, 'name': data['name'], 'kontakt': data.get('kontakt', '')}
        except Exception as e:
            api.abort(500, str(e))

    @lieferanten_ns.doc('delete_lieferant')
    def delete(self, lieferant_id):
        """Lieferanten löschen (nur wenn keine Artikel vorhanden)"""
        try:
            lieferant = inventory.lieferant_finden(lieferant_id)
            if not lieferant:
                api.abort(404, 'Lieferant nicht gefunden')
            
            success = inventory.lieferant_loeschen(lieferant_id)
            if not success:
                api.abort(400, 'Lieferant kann nicht gelöscht werden - Artikel vorhanden')
            
            return {'message': 'Lieferant erfolgreich gelöscht'}
        except Exception as e:
            api.abort(500, str(e))

# ARTIKEL ENDPOINTS
@artikel_ns.route('')
class ArtikelList(Resource):
    @artikel_ns.marshal_list_with(artikel_model)
    @artikel_ns.doc('list_artikel')
    def get(self):
        """Alle Artikel auflisten (mit Mindestmengen)"""
        try:
            artikel = inventory.artikel_auflisten()
            return [{
                'artikelnummer': a[0],
                'bezeichnung': a[1], 
                'lieferant_name': a[2],
                'mindestmenge': a[3]
            } for a in artikel]
        except Exception as e:
            api.abort(500, str(e))

    @artikel_ns.expect(artikel_input)
    @artikel_ns.marshal_with(artikel_input, code=201)
    @artikel_ns.doc('create_artikel')
    def post(self):
        """Neuen Artikel anlegen (mit Mindestmenge)"""
        try:
            data = request.get_json()
            required_fields = ['artikelnummer', 'bezeichnung', 'lieferant_id']
            
            if not data or not all(field in data for field in required_fields):
                api.abort(400, 'Artikelnummer, Bezeichnung und Lieferant-ID sind erforderlich')
            
            lieferant = inventory.lieferant_finden(data['lieferant_id'])
            if not lieferant:
                api.abort(400, 'Lieferant nicht gefunden')
                
            mindestmenge = data.get('mindestmenge', 1)
            success = inventory.artikel_hinzufuegen(
                data['artikelnummer'], data['bezeichnung'], 
                data['lieferant_id'], mindestmenge
            )
            
            if not success:
                api.abort(400, 'Artikel konnte nicht angelegt werden (bereits vorhanden?)')
            
            return {
                'artikelnummer': data['artikelnummer'],
                'bezeichnung': data['bezeichnung'],
                'lieferant_id': data['lieferant_id'],
                'mindestmenge': mindestmenge
            }, 201
        except Exception as e:
            api.abort(500, str(e))

@artikel_ns.route('/<string:artikelnummer>')
class ArtikelDetail(Resource):
    @artikel_ns.marshal_with(artikel_input)
    @artikel_ns.doc('get_artikel')
    def get(self, artikelnummer):
        """Artikel-Details abrufen"""
        try:
            artikel = inventory.artikel_finden(artikelnummer)
            if not artikel:
                api.abort(404, 'Artikel nicht gefunden')
            
            return {
                'artikelnummer': artikel.artikelnummer,
                'bezeichnung': artikel.bezeichnung,
                'lieferant_id': artikel.lieferant_id,
                'mindestmenge': artikel.mindestmenge
            }
        except Exception as e:
            api.abort(500, str(e))

# KUNDEN ENDPOINTS  
@kunden_ns.route('')
class KundenList(Resource):
    @kunden_ns.marshal_list_with(kunde_model)
    @kunden_ns.doc('list_kunden')
    def get(self):
        """Alle Kunden auflisten"""
        try:
            kunden = inventory.kunden_auflisten()
            return [{'id': k.id, 'name': k.name, 'kontakt': k.kontakt} for k in kunden]
        except Exception as e:
            api.abort(500, str(e))

    @kunden_ns.expect(kunde_input)
    @kunden_ns.marshal_with(kunde_model, code=201)
    @kunden_ns.doc('create_kunde')
    def post(self):
        """Neuen Kunden anlegen"""
        try:
            data = request.get_json()
            if not data or 'name' not in data:
                api.abort(400, 'Name ist erforderlich')
            
            kunde_id = inventory.kunde_hinzufuegen(
                data['name'], data.get('kontakt', '')
            )
            return {
                'id': kunde_id,
                'name': data['name'],
                'kontakt': data.get('kontakt', '')
            }, 201
        except Exception as e:
            api.abort(500, str(e))

@kunden_ns.route('/<int:kunde_id>')
class KundeDetail(Resource):
    @kunden_ns.marshal_with(kunde_model)
    @kunden_ns.doc('get_kunde')
    def get(self, kunde_id):
        """Kunden-Details abrufen"""
        try:
            kunde = inventory.kunde_finden(kunde_id)
            if not kunde:
                api.abort(404, 'Kunde nicht gefunden')
            return {'id': kunde.id, 'name': kunde.name, 'kontakt': kunde.kontakt}
        except Exception as e:
            api.abort(500, str(e))

# PROJEKTE ENDPOINTS
@projekte_ns.route('')
class ProjekteList(Resource):
    @projekte_ns.marshal_list_with(projekt_model)
    @projekte_ns.doc('list_projekte')
    def get(self):
        """Alle Projekte auflisten"""
        try:
            projekte = inventory.projekte_auflisten()
            return [{'id': p[0], 'projektname': p[1], 'kunde_name': p[2]} for p in projekte]
        except Exception as e:
            api.abort(500, str(e))

    @projekte_ns.expect(projekt_input)
    @projekte_ns.marshal_with(projekt_input, code=201)
    @projekte_ns.doc('create_projekt')
    def post(self):
        """Neues Projekt anlegen"""
        try:
            data = request.get_json()
            required_fields = ['projektname', 'kunde_id']
            
            if not data or not all(field in data for field in required_fields):
                api.abort(400, 'Projektname und Kunde-ID sind erforderlich')
            
            kunden = inventory.kunden_auflisten()
            kunde_ids = [k.id for k in kunden]
            if data['kunde_id'] not in kunde_ids:
                api.abort(400, 'Kunde nicht gefunden')
                
            projekt_id = inventory.projekt_hinzufuegen(
                data['projektname'], data['kunde_id']
            )
            return {
                'id': projekt_id,
                'projektname': data['projektname'],
                'kunde_id': data['kunde_id']
            }, 201
        except Exception as e:
            api.abort(500, str(e))

@projekte_ns.route('/<int:projekt_id>')
class ProjektDetail(Resource):
    @projekte_ns.doc('get_projekt_detail')
    def get(self, projekt_id):
        """Projekt-Details mit Verkäufen abrufen"""
        try:
            uebersicht = reports.projekt_uebersicht(projekt_id)
            if not uebersicht:
                api.abort(404, 'Projekt nicht gefunden')
            return uebersicht
        except Exception as e:
            api.abort(500, str(e))

# LAGER ENDPOINTS
@lager_ns.route('/eingang')
class Lagereingang(Resource):
    @lager_ns.expect(lagereingang_input)
    @lager_ns.doc('create_lagereingang')
    def post(self):
        """Wareneingang buchen (FIFO-Einlagerung)"""
        try:
            data = request.get_json()
            required_fields = ['artikelnummer', 'menge', 'einkaufspreis']
            
            if not data or not all(field in data for field in required_fields):
                api.abort(400, 'Artikelnummer, Menge und Einkaufspreis sind erforderlich')
            
            einlagerungsdatum = data.get('einlagerungsdatum', datetime.now().strftime("%Y-%m-%d"))
            
            success = inventory.lagereingang(
                data['artikelnummer'], data['menge'], 
                data['einkaufspreis'], einlagerungsdatum
            )
            
            if not success:
                api.abort(404, 'Artikel nicht gefunden')
            
            return {
                'message': 'Lagereingang erfolgreich',
                'artikelnummer': data['artikelnummer'],
                'menge': data['menge'],
                'einkaufspreis': data['einkaufspreis'],
                'einlagerungsdatum': einlagerungsdatum
            }, 201
        except Exception as e:
            api.abort(500, str(e))

@lager_ns.route('/bestand')
class Lagerbestand(Resource):
    @lager_ns.marshal_list_with(lagerbestand_model)
    @lager_ns.doc('get_lagerbestand')
    def get(self):
        """Gesamten Lagerbestand abrufen"""
        try:
            bestand = inventory.gesamter_lagerbestand()
            return [{
                'artikelnummer': b[0],
                'bezeichnung': b[1],
                'gesamtmenge': b[2],
                'durchschnittspreis': b[3]
            } for b in bestand]
        except Exception as e:
            api.abort(500, str(e))

@lager_ns.route('/bestand/<string:artikelnummer>')
class ArtikelLagerbestand(Resource):
    @lager_ns.doc('get_artikel_bestand', params={'include_zero': 'Auch Bestände mit 0 Menge anzeigen (true/false)'})
    def get(self, artikelnummer):
        """Lagerbestand für einen spezifischen Artikel abrufen"""
        try:
            include_zero = request.args.get('include_zero', 'false').lower() == 'true'
            bestaende = inventory.lagerbestand_artikel(artikelnummer, include_zero=include_zero)
            return [{
                'id': b.id,
                'verfuegbare_menge': b.verfuegbare_menge,
                'einkaufspreis': b.einkaufspreis,
                'einlagerungsdatum': b.einlagerungsdatum
            } for b in bestaende]
        except Exception as e:
            api.abort(500, str(e))

# VERKAUF ENDPOINTS
@verkauf_ns.route('')
class Verkauf(Resource):
    @verkauf_ns.expect(verkauf_input)
    @verkauf_ns.doc('create_verkauf')
    def post(self):
        """Verkauf buchen (FIFO-Abgang)"""
        try:
            data = request.get_json()
            required_fields = ['projekt_id', 'artikelnummer', 'verkaufte_menge', 'verkaufspreis']
            
            if not data or not all(field in data for field in required_fields):
                api.abort(400, 'Projekt-ID, Artikelnummer, Menge und Verkaufspreis sind erforderlich')
            
            projekte = inventory.projekte_auflisten()
            projekt_ids = [p[0] for p in projekte]
            if data['projekt_id'] not in projekt_ids:
                api.abort(400, 'Projekt nicht gefunden')
                
            verkaufsdatum = data.get('verkaufsdatum', datetime.now().strftime("%Y-%m-%d"))
            
            success = inventory.verkauf(
                data['projekt_id'], data['artikelnummer'],
                data['verkaufte_menge'], data['verkaufspreis'], verkaufsdatum
            )
            
            if not success:
                api.abort(400, 'Nicht genügend Artikel im Lager verfügbar')
            
            return {
                'message': 'Verkauf erfolgreich',
                'projekt_id': data['projekt_id'],
                'artikelnummer': data['artikelnummer'],
                'verkaufte_menge': data['verkaufte_menge'],
                'verkaufspreis': data['verkaufspreis'],
                'verkaufsdatum': verkaufsdatum
            }, 201
        except Exception as e:
            api.abort(500, str(e))

# BERICHTE ENDPOINTS
@berichte_ns.route('/mindestmenge')
class MindestmengenBericht(Resource):
    @berichte_ns.marshal_list_with(mindestmenge_model)
    @berichte_ns.doc('get_mindestmenge_bericht')
    def get(self):
        """Artikel unter Mindestmenge anzeigen"""
        try:
            artikel = inventory.artikel_unter_mindestmenge()
            return [{
                'artikelnummer': a[0],
                'bezeichnung': a[1],
                'mindestmenge': a[2],
                'aktueller_bestand': a[3],
                'lieferant_name': a[4],
                'nachbestellmenge': max(0, a[2] - a[3])
            } for a in artikel]
        except Exception as e:
            api.abort(500, str(e))

@berichte_ns.route('/lagerbestand')
class LagerbestandBericht(Resource):
    @berichte_ns.doc('get_lagerbestand_bericht', params={'detailliert': 'Detaillierte Ansicht (true/false)'})
    def get(self):
        """Lagerbestand-Bericht (zusammengefasst oder detailliert)"""
        try:
            detailliert = request.args.get('detailliert', 'false').lower() == 'true'
            
            if detailliert:
                bestand = reports.lagerbestand_detailliert()
            else:
                bestand = reports.lagerbestand_zusammenfassung()
            
            return bestand
        except Exception as e:
            api.abort(500, str(e))

@berichte_ns.route('/projekte')
class ProjekteBericht(Resource):
    @berichte_ns.doc('get_projekte_bericht')
    def get(self):
        """Übersicht aller Projekte mit Umsätzen"""
        try:
            projekte = reports.alle_projekte_uebersicht()
            return projekte
        except Exception as e:
            api.abort(500, str(e))

@berichte_ns.route('/gewinn')
class GewinnAnalyse(Resource):
    @berichte_ns.doc('get_gewinn_analyse', params={'projekt_id': 'Spezifische Projekt-ID (optional)'})
    def get(self):
        """Gewinn-Analyse (gesamt oder für spezifisches Projekt)"""
        try:
            projekt_id = request.args.get('projekt_id', type=int)
            analyse = reports.gewinn_analyse(projekt_id)
            return analyse
        except Exception as e:
            api.abort(500, str(e))

@berichte_ns.route('/lagerumschlag')
class LagerumschlagBericht(Resource):
    @berichte_ns.doc('get_lagerumschlag')
    def get(self):
        """Lagerumschlag-Analyse"""
        try:
            umschlag = reports.lagerumschlag()
            return umschlag
        except Exception as e:
            api.abort(500, str(e))

@api.route('/api/status')
class Status(Resource):
    @api.doc('get_status')
    def get(self):
        """API Status abrufen"""
        return {
            'status': 'ok',
            'message': 'Lagerverwaltung Backend API',
            'version': '1.0',
            'swagger_ui': '/swagger/'
        }

if __name__ == '__main__':
    print("🚀 Lagerverwaltung API mit Swagger UI")
    print("📊 Swagger UI verfügbar unter: http://localhost:5000/swagger/")
    print("🔧 API Status: http://localhost:5000/api/status")
    app.run(debug=True, host='0.0.0.0', port=5000)