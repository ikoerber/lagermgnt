from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from datetime import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from inventory_manager import InventoryManager
from reports import ReportGenerator
from auth_service import AuthService
from logger_config import app_logger
from exceptions import (
    LagerverwaltungError, LieferantError, ArtikelError, LagerError, 
    VerkaufError, ValidationError, NotFoundError, IntegrityError
)

app = Flask(__name__)
CORS(app)

# JWT Konfiguration
app.config['JWT_SECRET_KEY'] = 'your-super-secret-jwt-key-change-in-production'  # In Produktion ändern!
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Wird durch AuthService gesteuert
jwt = JWTManager(app)

app_logger.info("Starte Lagerverwaltung API")
inventory = InventoryManager()
reports = ReportGenerator()
auth_service = AuthService()
app_logger.info("API-Server erfolgreich initialisiert")

# JWT Callbacks
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    """Prüfe ob Token auf der Blacklist steht"""
    jti = jwt_payload['jti']
    return auth_service.is_token_blacklisted(jti)

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    app_logger.warning(f"Abgelaufener Token verwendet: {jwt_payload.get('sub', 'unknown')}")
    return jsonify({'error': 'Token ist abgelaufen', 'type': 'token_expired'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    app_logger.warning(f"Ungültiger Token: {error}")
    return jsonify({'error': 'Ungültiger Token', 'type': 'invalid_token'}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    app_logger.info(f"Fehlender Token: {error}")
    return jsonify({'error': 'Authorization Token erforderlich', 'type': 'missing_token'}), 401

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    app_logger.warning(f"Widerrufener Token verwendet: {jwt_payload.get('sub', 'unknown')}")
    return jsonify({'error': 'Token wurde widerrufen', 'type': 'token_revoked'}), 401

# Error Handler für Custom Exceptions
@app.errorhandler(ValidationError)
def handle_validation_error(error):
    app_logger.warning(f"Validierungsfehler: {error.message}")
    return jsonify({'error': error.message, 'type': 'validation_error'}), 400

@app.errorhandler(NotFoundError)
def handle_not_found_error(error):
    app_logger.info(f"Ressource nicht gefunden: {error.message}")
    return jsonify({'error': error.message, 'type': 'not_found_error'}), 404

@app.errorhandler(IntegrityError)
def handle_integrity_error(error):
    app_logger.warning(f"Integritätsfehler: {error.message}")
    return jsonify({'error': error.message, 'type': 'integrity_error'}), 409

@app.errorhandler(LagerverwaltungError)
def handle_lagerverwaltung_error(error):
    app_logger.error(f"Anwendungsfehler: {error.message}")
    return jsonify({'error': error.message, 'type': 'application_error'}), 500

@app.errorhandler(404)
def not_found(error):
    app_logger.info(f"404 Fehler: {request.url}")
    return jsonify({'error': 'Endpoint nicht gefunden'}), 404

@app.errorhandler(500)
def internal_error(error):
    app_logger.error(f"Interner Serverfehler: {error}")
    return jsonify({'error': 'Interner Serverfehler'}), 500

# Authentication API
@app.route('/api/auth/register', methods=['POST'])
def register():
    """Erstelle neuen User (nur für Admin/Setup)"""
    app_logger.debug("POST /api/auth/register aufgerufen")
    data = request.get_json(force=True, silent=True)
    if data is None:
        raise ValidationError('JSON-Daten erforderlich')
    if not data.get('username'):
        raise ValidationError('Username ist erforderlich')
    if not data.get('password'):
        raise ValidationError('Passwort ist erforderlich')
    
    user_id = auth_service.create_user(data['username'], data['password'])
    user = auth_service.find_user_by_id(user_id)
    
    return jsonify({
        'message': 'User erfolgreich erstellt',
        'user': user.to_dict()
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User Login mit Username/Password"""
    app_logger.debug("POST /api/auth/login aufgerufen")
    data = request.get_json(force=True, silent=True)
    if data is None:
        raise ValidationError('JSON-Daten erforderlich')
    if not data.get('username'):
        raise ValidationError('Username ist erforderlich')
    if not data.get('password'):
        raise ValidationError('Passwort ist erforderlich')
    
    user = auth_service.authenticate_user(data['username'], data['password'])
    if not user:
        app_logger.warning(f"Login fehlgeschlagen für Username: {data['username']}")
        return jsonify({
            'error': 'Ungültige Anmeldedaten',
            'type': 'authentication_failed'
        }), 401
    
    tokens = auth_service.create_tokens(user)
    return jsonify(tokens)

@app.route('/api/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh Access Token"""
    app_logger.debug("POST /api/auth/refresh aufgerufen")
    current_user_id = get_jwt_identity()
    user = auth_service.find_user_by_id(int(current_user_id))
    
    if not user:
        raise NotFoundError('User nicht gefunden')
    
    tokens = auth_service.create_tokens(user)
    return jsonify(tokens)

@app.route('/api/auth/logout', methods=['DELETE'])
@jwt_required()
def logout():
    """User Logout - Token zur Blacklist hinzufügen"""
    app_logger.debug("DELETE /api/auth/logout aufgerufen")
    jti = get_jwt()['jti']
    current_user_id = get_jwt_identity()
    
    auth_service.blacklist_token(jti)
    app_logger.info(f"User {current_user_id} erfolgreich ausgeloggt")
    
    return jsonify({
        'message': 'Erfolgreich ausgeloggt'
    })

@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Aktuelle User-Informationen abrufen"""
    app_logger.debug("GET /api/auth/me aufgerufen")
    current_user_id = get_jwt_identity()
    user = auth_service.find_user_by_id(int(current_user_id))
    
    if not user:
        raise NotFoundError('User nicht gefunden')
    
    return jsonify(user.to_dict())

@app.route('/api/auth/users', methods=['GET'])
@jwt_required()
def get_users():
    """Liste aller User (nur für authentifizierte User)"""
    app_logger.debug("GET /api/auth/users aufgerufen")
    users = auth_service.list_users()
    return jsonify(users)

# Lieferanten API
@app.route('/api/lieferanten', methods=['GET'])
@jwt_required()
def get_lieferanten():
    app_logger.debug("GET /api/lieferanten aufgerufen")
    try:
        lieferanten = inventory.lieferanten_auflisten()
        return jsonify([{
            'id': l.id,
            'name': l.name,
            'kontakt': l.kontakt
        } for l in lieferanten])
    except Exception as e:
        app_logger.error(f"Unerwarteter Fehler bei GET /api/lieferanten: {e}")
        return jsonify({'error': 'Interner Serverfehler'}), 500

@app.route('/api/lieferanten', methods=['POST'])
@jwt_required()
def create_lieferant():
    app_logger.debug("POST /api/lieferanten aufgerufen")
    data = request.get_json(force=True, silent=True)
    if data is None:
        raise ValidationError('JSON-Daten erforderlich')
    if not data or 'name' not in data:
        raise ValidationError('Name ist erforderlich')
    
    lieferant_id = inventory.lieferant_hinzufuegen(
        data['name'], 
        data.get('kontakt', '')
    )
    return jsonify({
        'id': lieferant_id,
        'name': data['name'],
        'kontakt': data.get('kontakt', '')
    }), 201

@app.route('/api/lieferanten/<int:lieferant_id>', methods=['GET'])
@jwt_required()
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
@jwt_required()
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
@jwt_required()
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
@jwt_required()
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
@jwt_required()
def create_artikel():
    app_logger.debug("POST /api/artikel aufgerufen")
    data = request.get_json(force=True, silent=True)
    if data is None:
        raise ValidationError('JSON-Daten erforderlich')
    
    required_fields = ['artikelnummer', 'bezeichnung', 'lieferant_id']
    if not data or not all(field in data for field in required_fields):
        raise ValidationError('Artikelnummer, Bezeichnung und Lieferant-ID sind erforderlich')
    
    mindestmenge = data.get('mindestmenge', 1)
    
    # Die Validierung passiert jetzt in inventory_manager.artikel_hinzufuegen()
    success = inventory.artikel_hinzufuegen(
        data['artikelnummer'],
        data['bezeichnung'],
        data['lieferant_id'],
        mindestmenge
    )
    
    return jsonify({
        'artikelnummer': data['artikelnummer'],
        'bezeichnung': data['bezeichnung'],
        'lieferant_id': data['lieferant_id'],
        'mindestmenge': mindestmenge
    }), 201

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