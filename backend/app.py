from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import get_config
from auth_service import AuthService
from logger_config import app_logger
from exceptions import (
    LagerverwaltungError, LieferantError, ArtikelError, LagerError, 
    VerkaufError, ValidationError, NotFoundError, IntegrityError
)
from api import register_blueprints

# Load configuration
config = get_config()

app = Flask(__name__)
app.config.from_object(config)
CORS(app, origins=config.CORS_ORIGINS)

# JWT Configuration from secure config
jwt = JWTManager(app)

app_logger.info("Starte Lagerverwaltung API")
auth_service = AuthService()

# Register all API blueprints
register_blueprints(app)
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

# Status API (remains in main app)
@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({
        'status': 'ok',
        'message': 'Lagerverwaltung Backend API',
        'version': '1.0'
    })

if __name__ == '__main__':
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)