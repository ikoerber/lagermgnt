from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from datetime import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import get_config
from inventory_manager import InventoryManager
from reports import ReportGenerator
from auth_service import AuthService
from logger_config import app_logger
from exceptions import (
    LagerverwaltungError, LieferantError, ArtikelError, LagerError, 
    VerkaufError, ValidationError, NotFoundError, IntegrityError
)

# Load configuration
config = get_config()

app = Flask(__name__)
app.config.from_object(config)
CORS(app, origins=config.CORS_ORIGINS)

# JWT Configuration from secure config
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
    lieferant = inventory.lieferant_finden(lieferant_id)
    if not lieferant:
        raise NotFoundError('Lieferant nicht gefunden')
    
    return jsonify({
        'id': lieferant.id,
        'name': lieferant.name,
        'kontakt': lieferant.kontakt
    })

@app.route('/api/lieferanten/<int:lieferant_id>', methods=['PUT'])
@jwt_required()
def update_lieferant(lieferant_id):
    data = request.get_json(force=True, silent=True)
    if data is None:
        raise ValidationError('JSON-Daten erforderlich')
    if not data or 'name' not in data:
        raise ValidationError('Name ist erforderlich')
    
    # Lieferant aktualisieren (includes existence check)
    inventory.lieferant_aktualisieren(
        lieferant_id,
        data['name'], 
        data.get('kontakt', '')
    )
    
    return jsonify({
        'id': lieferant_id,
        'name': data['name'],
        'kontakt': data.get('kontakt', '')
    })

@app.route('/api/lieferanten/<int:lieferant_id>', methods=['DELETE'])
@jwt_required()
def delete_lieferant(lieferant_id):
    # Lieferant löschen (includes existence and constraint checks)
    inventory.lieferant_loeschen(lieferant_id)
    
    return jsonify({'message': 'Lieferant erfolgreich gelöscht'})

# Artikel API
@app.route('/api/artikel', methods=['GET'])
@jwt_required()
def get_artikel():
    artikel = inventory.artikel_auflisten()
    return jsonify([{
        'artikelnummer': a[0],
        'bezeichnung': a[1],
        'lieferant_name': a[2],
        'mindestmenge': a[3]
    } for a in artikel])

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
@jwt_required()
def get_artikel_detail(artikelnummer):
    artikel = inventory.artikel_finden(artikelnummer)
    if not artikel:
        raise NotFoundError('Artikel nicht gefunden')
    
    return jsonify({
        'artikelnummer': artikel.artikelnummer,
        'bezeichnung': artikel.bezeichnung,
        'lieferant_id': artikel.lieferant_id,
        'mindestmenge': artikel.mindestmenge
    })

# Kunden API
@app.route('/api/kunden', methods=['GET'])
@jwt_required()
def get_kunden():
    kunden = inventory.kunden_auflisten()
    return jsonify([{
        'id': k.id,
        'name': k.name,
        'kontakt': k.kontakt
    } for k in kunden])

@app.route('/api/kunden', methods=['POST'])
@jwt_required()
def create_kunde():
    data = request.get_json(force=True, silent=True)
    if data is None:
        raise ValidationError('JSON-Daten erforderlich')
    if not data or 'name' not in data:
        raise ValidationError('Name ist erforderlich')
    
    kunde_id = inventory.kunde_hinzufuegen(
        data['name'],
        data.get('kontakt', '')
    )
    return jsonify({
        'id': kunde_id,
        'name': data['name'],
        'kontakt': data.get('kontakt', '')
    }), 201

@app.route('/api/kunden/<int:kunde_id>', methods=['GET'])
@jwt_required()
def get_kunde_detail(kunde_id):
    kunde = inventory.kunde_finden(kunde_id)
    if not kunde:
        raise NotFoundError('Kunde nicht gefunden')
    
    return jsonify({
        'id': kunde.id,
        'name': kunde.name,
        'kontakt': kunde.kontakt
    })

# Projekte API
@app.route('/api/projekte', methods=['GET'])
@jwt_required()
def get_projekte():
    projekte = inventory.projekte_auflisten()
    return jsonify([{
        'id': p[0],
        'projektname': p[1],
        'kunde_name': p[2]
    } for p in projekte])

@app.route('/api/projekte', methods=['POST'])
@jwt_required()
def create_projekt():
    data = request.get_json(force=True, silent=True)
    if data is None:
        raise ValidationError('JSON-Daten erforderlich')
    
    required_fields = ['projektname', 'kunde_id']
    
    if not data or not all(field in data for field in required_fields):
        raise ValidationError('Projektname und Kunde-ID sind erforderlich')
    
    # Prüfen ob Kunde existiert
    kunde = inventory.kunde_finden(data['kunde_id'])
    if not kunde:
        raise NotFoundError('Kunde nicht gefunden')
        
    projekt_id = inventory.projekt_hinzufuegen(
        data['projektname'],
        data['kunde_id']
    )
    return jsonify({
        'id': projekt_id,
        'projektname': data['projektname'],
        'kunde_id': data['kunde_id']
    }), 201

@app.route('/api/projekte/<int:projekt_id>', methods=['GET'])
@jwt_required()
def get_projekt_detail(projekt_id):
    uebersicht = reports.projekt_uebersicht(projekt_id)
    if not uebersicht:
        raise NotFoundError('Projekt nicht gefunden')
    
    return jsonify(uebersicht)

# Lager API
@app.route('/api/lager/eingang', methods=['POST'])
@jwt_required()
def lagereingang():
    data = request.get_json(force=True, silent=True)
    if data is None:
        raise ValidationError('JSON-Daten erforderlich')
    
    required_fields = ['artikelnummer', 'menge', 'einkaufspreis']
    
    if not data or not all(field in data for field in required_fields):
        raise ValidationError('Artikelnummer, Menge und Einkaufspreis sind erforderlich')
    
    einlagerungsdatum = data.get('einlagerungsdatum', datetime.now().strftime("%Y-%m-%d"))
    
    success = inventory.lagereingang(
        data['artikelnummer'],
        data['menge'],
        data['einkaufspreis'],
        einlagerungsdatum
    )
    
    if not success:
        raise NotFoundError('Artikel nicht gefunden')
    
    return jsonify({
        'message': 'Lagereingang erfolgreich',
        'artikelnummer': data['artikelnummer'],
        'menge': data['menge'],
        'einkaufspreis': data['einkaufspreis'],
        'einlagerungsdatum': einlagerungsdatum
    }), 201

@app.route('/api/lager/bestand', methods=['GET'])
@jwt_required()
def get_lagerbestand():
    bestand = inventory.gesamter_lagerbestand()
    return jsonify([{
        'artikelnummer': b[0],
        'bezeichnung': b[1],
        'gesamtmenge': b[2],
        'durchschnittspreis': b[3]
    } for b in bestand])

@app.route('/api/lager/bestand/<artikelnummer>', methods=['GET'])
@jwt_required()
def get_artikel_lagerbestand(artikelnummer):
    include_zero = request.args.get('include_zero', 'false').lower() == 'true'
    bestaende = inventory.lagerbestand_artikel(artikelnummer, include_zero=include_zero)
    return jsonify([{
        'id': b.id,
        'verfuegbare_menge': b.verfuegbare_menge,
        'einkaufspreis': b.einkaufspreis,
        'einlagerungsdatum': b.einlagerungsdatum
    } for b in bestaende])

# Verkauf API
@app.route('/api/verkauf', methods=['POST'])
@jwt_required()
def verkauf():
    data = request.get_json(force=True, silent=True)
    if data is None:
        raise ValidationError('JSON-Daten erforderlich')
    
    required_fields = ['projekt_id', 'artikelnummer', 'verkaufte_menge', 'verkaufspreis']
    
    if not data or not all(field in data for field in required_fields):
        raise ValidationError('Projekt-ID, Artikelnummer, Menge und Verkaufspreis sind erforderlich')
    
    # Prüfen ob Projekt existiert
    projekte = inventory.projekte_auflisten()
    projekt_ids = [p[0] for p in projekte]
    if data['projekt_id'] not in projekt_ids:
        raise NotFoundError('Projekt nicht gefunden')
        
    verkaufsdatum = data.get('verkaufsdatum', datetime.now().strftime("%Y-%m-%d"))
    
    success = inventory.verkauf(
        data['projekt_id'],
        data['artikelnummer'],
        data['verkaufte_menge'],
        data['verkaufspreis'],
        verkaufsdatum
    )
    
    if not success:
        raise LagerError('Nicht genügend Artikel im Lager verfügbar')
    
    return jsonify({
        'message': 'Verkauf erfolgreich',
        'projekt_id': data['projekt_id'],
        'artikelnummer': data['artikelnummer'],
        'verkaufte_menge': data['verkaufte_menge'],
        'verkaufspreis': data['verkaufspreis'],
        'verkaufsdatum': verkaufsdatum
    }), 201

# Berichte API
@app.route('/api/berichte/lagerbestand', methods=['GET'])
@jwt_required()
def get_lagerbestand_detailliert():
    detailliert = request.args.get('detailliert', 'false').lower() == 'true'
    
    if detailliert:
        bestand = reports.lagerbestand_detailliert()
    else:
        bestand = reports.lagerbestand_zusammenfassung()
    
    return jsonify(bestand)

@app.route('/api/berichte/projekte', methods=['GET'])
@jwt_required()
def get_alle_projekte_bericht():
    projekte = reports.alle_projekte_uebersicht()
    return jsonify(projekte)

@app.route('/api/berichte/gewinn', methods=['GET'])
@jwt_required()
def get_gewinn_analyse():
    projekt_id = request.args.get('projekt_id', type=int)
    analyse = reports.gewinn_analyse(projekt_id)
    return jsonify(analyse)

@app.route('/api/berichte/lagerumschlag', methods=['GET'])
@jwt_required()
def get_lagerumschlag():
    umschlag = reports.lagerumschlag()
    return jsonify(umschlag)

@app.route('/api/berichte/mindestmenge', methods=['GET'])
@jwt_required()
def get_artikel_unter_mindestmenge():
    artikel = inventory.artikel_unter_mindestmenge()
    return jsonify([{
        'artikelnummer': a[0],
        'bezeichnung': a[1],
        'mindestmenge': a[2],
        'aktueller_bestand': a[3],
        'lieferant_name': a[4],
        'nachbestellmenge': max(0, a[2] - a[3])
    } for a in artikel])

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({
        'status': 'ok',
        'message': 'Lagerverwaltung Backend API',
        'version': '1.0'
    })

if __name__ == '__main__':
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)