from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from inventory_manager import InventoryManager
from logger_config import app_logger
from exceptions import ValidationError, NotFoundError

lieferanten_bp = Blueprint('lieferanten', __name__)
inventory = InventoryManager()

@lieferanten_bp.route('', methods=['GET'])
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

@lieferanten_bp.route('', methods=['POST'])
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

@lieferanten_bp.route('/<int:lieferant_id>', methods=['GET'])
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

@lieferanten_bp.route('/<int:lieferant_id>', methods=['PUT'])
@jwt_required()
def update_lieferant(lieferant_id):
    data = request.get_json(force=True, silent=True)
    if data is None:
        raise ValidationError('JSON-Daten erforderlich')
    if not data or 'name' not in data:
        raise ValidationError('Name ist erforderlich')
    
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

@lieferanten_bp.route('/<int:lieferant_id>', methods=['DELETE'])
@jwt_required()
def delete_lieferant(lieferant_id):
    inventory.lieferant_loeschen(lieferant_id)
    return jsonify({'message': 'Lieferant erfolgreich gelöscht'})