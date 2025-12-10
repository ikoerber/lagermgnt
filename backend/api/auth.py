from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from auth_service import AuthService
from logger_config import app_logger
from exceptions import ValidationError, NotFoundError

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService()

@auth_bp.route('/register', methods=['POST'])
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

@auth_bp.route('/login', methods=['POST'])
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

@auth_bp.route('/refresh', methods=['POST'])
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

@auth_bp.route('/logout', methods=['DELETE'])
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

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Aktuelle User-Informationen abrufen"""
    app_logger.debug("GET /api/auth/me aufgerufen")
    current_user_id = get_jwt_identity()
    user = auth_service.find_user_by_id(int(current_user_id))
    
    if not user:
        raise NotFoundError('User nicht gefunden')
    
    return jsonify(user.to_dict())

@auth_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """Liste aller User (nur für authentifizierte User)"""
    app_logger.debug("GET /api/auth/users aufgerufen")
    users = auth_service.list_users()
    return jsonify(users)