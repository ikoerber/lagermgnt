from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from inventory_manager import InventoryManager
from reports import ReportGenerator

app = Flask(__name__)
CORS(app)

inventory = InventoryManager()
reports = ReportGenerator()

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint nicht gefunden'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Interner Serverfehler'}), 500

# Lieferanten API
@app.route('/api/lieferanten', methods=['GET'])
def get_lieferanten():
    try:
        lieferanten = inventory.lieferanten_auflisten()
        return jsonify([{
            'id': l.id,
            'name': l.name,
            'kontakt': l.kontakt
        } for l in lieferanten])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/lieferanten', methods=['POST'])
def create_lieferant():
    try:
        data = request.get_json(force=True, silent=True)
        if data is None:
            return jsonify({'error': 'JSON-Daten erforderlich'}), 400
        if not data or 'name' not in data:
            return jsonify({'error': 'Name ist erforderlich'}), 400
        
        lieferant_id = inventory.lieferant_hinzufuegen(
            data['name'], 
            data.get('kontakt', '')
        )
        return jsonify({
            'id': lieferant_id,
            'name': data['name'],
            'kontakt': data.get('kontakt', '')
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/lieferanten/<int:lieferant_id>', methods=['GET'])
def get_lieferant(lieferant_id):
    try:
        lieferant = inventory.lieferant_finden(lieferant_id)
        if not lieferant:
            return jsonify({'error': 'Lieferant nicht gefunden'}), 404
        
        return jsonify({
            'id': lieferant.id,
            'name': lieferant.name,
            'kontakt': lieferant.kontakt
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/lieferanten/<int:lieferant_id>', methods=['PUT'])
def update_lieferant(lieferant_id):
    try:
        data = request.get_json(force=True, silent=True)
        if data is None:
            return jsonify({'error': 'JSON-Daten erforderlich'}), 400
        if not data or 'name' not in data:
            return jsonify({'error': 'Name ist erforderlich'}), 400
        
        # Prüfen ob Lieferant existiert
        lieferant = inventory.lieferant_finden(lieferant_id)
        if not lieferant:
            return jsonify({'error': 'Lieferant nicht gefunden'}), 404
        
        success = inventory.lieferant_aktualisieren(
            lieferant_id,
            data['name'], 
            data.get('kontakt', '')
        )
        
        if not success:
            return jsonify({'error': 'Lieferant konnte nicht aktualisiert werden'}), 400
        
        return jsonify({
            'id': lieferant_id,
            'name': data['name'],
            'kontakt': data.get('kontakt', '')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/lieferanten/<int:lieferant_id>', methods=['DELETE'])
def delete_lieferant(lieferant_id):
    try:
        # Prüfen ob Lieferant existiert
        lieferant = inventory.lieferant_finden(lieferant_id)
        if not lieferant:
            return jsonify({'error': 'Lieferant nicht gefunden'}), 404
        
        success = inventory.lieferant_loeschen(lieferant_id)
        
        if not success:
            return jsonify({'error': 'Lieferant kann nicht gelöscht werden - Artikel vorhanden'}), 400
        
        return jsonify({'message': 'Lieferant erfolgreich gelöscht'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Artikel API
@app.route('/api/artikel', methods=['GET'])
def get_artikel():
    try:
        artikel = inventory.artikel_auflisten()
        return jsonify([{
            'artikelnummer': a[0],
            'bezeichnung': a[1],
            'lieferant_name': a[2],
            'mindestmenge': a[3]
        } for a in artikel])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/artikel', methods=['POST'])
def create_artikel():
    try:
        data = request.get_json(force=True, silent=True)
        if data is None:
            return jsonify({'error': 'JSON-Daten erforderlich'}), 400
        
        required_fields = ['artikelnummer', 'bezeichnung', 'lieferant_id']
        
        if not data or not all(field in data for field in required_fields):
            return jsonify({'error': 'Artikelnummer, Bezeichnung und Lieferant-ID sind erforderlich'}), 400
        
        # Prüfen ob Lieferant existiert
        lieferant = inventory.lieferant_finden(data['lieferant_id'])
        if not lieferant:
            return jsonify({'error': 'Lieferant nicht gefunden'}), 400
            
        mindestmenge = data.get('mindestmenge', 1)
        success = inventory.artikel_hinzufuegen(
            data['artikelnummer'],
            data['bezeichnung'],
            data['lieferant_id'],
            mindestmenge
        )
        
        if not success:
            return jsonify({'error': 'Artikel konnte nicht angelegt werden (bereits vorhanden?)'}), 400
        
        return jsonify({
            'artikelnummer': data['artikelnummer'],
            'bezeichnung': data['bezeichnung'],
            'lieferant_id': data['lieferant_id'],
            'mindestmenge': mindestmenge
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/artikel/<artikelnummer>', methods=['GET'])
def get_artikel_detail(artikelnummer):
    try:
        artikel = inventory.artikel_finden(artikelnummer)
        if not artikel:
            return jsonify({'error': 'Artikel nicht gefunden'}), 404
        
        return jsonify({
            'artikelnummer': artikel.artikelnummer,
            'bezeichnung': artikel.bezeichnung,
            'lieferant_id': artikel.lieferant_id,
            'mindestmenge': artikel.mindestmenge
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Kunden API
@app.route('/api/kunden', methods=['GET'])
def get_kunden():
    try:
        kunden = inventory.kunden_auflisten()
        return jsonify([{
            'id': k.id,
            'name': k.name,
            'kontakt': k.kontakt
        } for k in kunden])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/kunden', methods=['POST'])
def create_kunde():
    try:
        data = request.get_json(force=True, silent=True)
        if data is None:
            return jsonify({'error': 'JSON-Daten erforderlich'}), 400
        if not data or 'name' not in data:
            return jsonify({'error': 'Name ist erforderlich'}), 400
        
        kunde_id = inventory.kunde_hinzufuegen(
            data['name'],
            data.get('kontakt', '')
        )
        return jsonify({
            'id': kunde_id,
            'name': data['name'],
            'kontakt': data.get('kontakt', '')
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/kunden/<int:kunde_id>', methods=['GET'])
def get_kunde_detail(kunde_id):
    try:
        kunde = inventory.kunde_finden(kunde_id)
        if not kunde:
            return jsonify({'error': 'Kunde nicht gefunden'}), 404
        
        return jsonify({
            'id': kunde.id,
            'name': kunde.name,
            'kontakt': kunde.kontakt
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Projekte API
@app.route('/api/projekte', methods=['GET'])
def get_projekte():
    try:
        projekte = inventory.projekte_auflisten()
        return jsonify([{
            'id': p[0],
            'projektname': p[1],
            'kunde_name': p[2]
        } for p in projekte])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/projekte', methods=['POST'])
def create_projekt():
    try:
        data = request.get_json(force=True, silent=True)
        if data is None:
            return jsonify({'error': 'JSON-Daten erforderlich'}), 400
        
        required_fields = ['projektname', 'kunde_id']
        
        if not data or not all(field in data for field in required_fields):
            return jsonify({'error': 'Projektname und Kunde-ID sind erforderlich'}), 400
        
        # Prüfen ob Kunde existiert
        kunden = inventory.kunden_auflisten()
        kunde_ids = [k.id for k in kunden]
        if data['kunde_id'] not in kunde_ids:
            return jsonify({'error': 'Kunde nicht gefunden'}), 400
            
        projekt_id = inventory.projekt_hinzufuegen(
            data['projektname'],
            data['kunde_id']
        )
        return jsonify({
            'id': projekt_id,
            'projektname': data['projektname'],
            'kunde_id': data['kunde_id']
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/projekte/<int:projekt_id>', methods=['GET'])
def get_projekt_detail(projekt_id):
    try:
        uebersicht = reports.projekt_uebersicht(projekt_id)
        if not uebersicht:
            return jsonify({'error': 'Projekt nicht gefunden'}), 404
        
        return jsonify(uebersicht)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Lager API
@app.route('/api/lager/eingang', methods=['POST'])
def lagereingang():
    try:
        data = request.get_json(force=True, silent=True)
        if data is None:
            return jsonify({'error': 'JSON-Daten erforderlich'}), 400
        
        required_fields = ['artikelnummer', 'menge', 'einkaufspreis']
        
        if not data or not all(field in data for field in required_fields):
            return jsonify({'error': 'Artikelnummer, Menge und Einkaufspreis sind erforderlich'}), 400
        
        einlagerungsdatum = data.get('einlagerungsdatum', datetime.now().strftime("%Y-%m-%d"))
        
        success = inventory.lagereingang(
            data['artikelnummer'],
            data['menge'],
            data['einkaufspreis'],
            einlagerungsdatum
        )
        
        if not success:
            return jsonify({'error': 'Artikel nicht gefunden'}), 404
        
        return jsonify({
            'message': 'Lagereingang erfolgreich',
            'artikelnummer': data['artikelnummer'],
            'menge': data['menge'],
            'einkaufspreis': data['einkaufspreis'],
            'einlagerungsdatum': einlagerungsdatum
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/lager/bestand', methods=['GET'])
def get_lagerbestand():
    try:
        bestand = inventory.gesamter_lagerbestand()
        return jsonify([{
            'artikelnummer': b[0],
            'bezeichnung': b[1],
            'gesamtmenge': b[2],
            'durchschnittspreis': b[3]
        } for b in bestand])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/lager/bestand/<artikelnummer>', methods=['GET'])
def get_artikel_lagerbestand(artikelnummer):
    try:
        include_zero = request.args.get('include_zero', 'false').lower() == 'true'
        bestaende = inventory.lagerbestand_artikel(artikelnummer, include_zero=include_zero)
        return jsonify([{
            'id': b.id,
            'verfuegbare_menge': b.verfuegbare_menge,
            'einkaufspreis': b.einkaufspreis,
            'einlagerungsdatum': b.einlagerungsdatum
        } for b in bestaende])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Verkauf API
@app.route('/api/verkauf', methods=['POST'])
def verkauf():
    try:
        data = request.get_json(force=True, silent=True)
        if data is None:
            return jsonify({'error': 'JSON-Daten erforderlich'}), 400
        
        required_fields = ['projekt_id', 'artikelnummer', 'verkaufte_menge', 'verkaufspreis']
        
        if not data or not all(field in data for field in required_fields):
            return jsonify({'error': 'Projekt-ID, Artikelnummer, Menge und Verkaufspreis sind erforderlich'}), 400
        
        # Prüfen ob Projekt existiert
        projekte = inventory.projekte_auflisten()
        projekt_ids = [p[0] for p in projekte]
        if data['projekt_id'] not in projekt_ids:
            return jsonify({'error': 'Projekt nicht gefunden'}), 400
            
        verkaufsdatum = data.get('verkaufsdatum', datetime.now().strftime("%Y-%m-%d"))
        
        success = inventory.verkauf(
            data['projekt_id'],
            data['artikelnummer'],
            data['verkaufte_menge'],
            data['verkaufspreis'],
            verkaufsdatum
        )
        
        if not success:
            return jsonify({'error': 'Nicht genügend Artikel im Lager verfügbar'}), 400
        
        return jsonify({
            'message': 'Verkauf erfolgreich',
            'projekt_id': data['projekt_id'],
            'artikelnummer': data['artikelnummer'],
            'verkaufte_menge': data['verkaufte_menge'],
            'verkaufspreis': data['verkaufspreis'],
            'verkaufsdatum': verkaufsdatum
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Berichte API
@app.route('/api/berichte/lagerbestand', methods=['GET'])
def get_lagerbestand_detailliert():
    try:
        detailliert = request.args.get('detailliert', 'false').lower() == 'true'
        
        if detailliert:
            bestand = reports.lagerbestand_detailliert()
        else:
            bestand = reports.lagerbestand_zusammenfassung()
        
        return jsonify(bestand)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/berichte/projekte', methods=['GET'])
def get_alle_projekte_bericht():
    try:
        projekte = reports.alle_projekte_uebersicht()
        return jsonify(projekte)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/berichte/gewinn', methods=['GET'])
def get_gewinn_analyse():
    try:
        projekt_id = request.args.get('projekt_id', type=int)
        analyse = reports.gewinn_analyse(projekt_id)
        return jsonify(analyse)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/berichte/lagerumschlag', methods=['GET'])
def get_lagerumschlag():
    try:
        umschlag = reports.lagerumschlag()
        return jsonify(umschlag)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/berichte/mindestmenge', methods=['GET'])
def get_artikel_unter_mindestmenge():
    try:
        artikel = inventory.artikel_unter_mindestmenge()
        return jsonify([{
            'artikelnummer': a[0],
            'bezeichnung': a[1],
            'mindestmenge': a[2],
            'aktueller_bestand': a[3],
            'lieferant_name': a[4],
            'nachbestellmenge': max(0, a[2] - a[3])
        } for a in artikel])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({
        'status': 'ok',
        'message': 'Lagerverwaltung Backend API',
        'version': '1.0'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)