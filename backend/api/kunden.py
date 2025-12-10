from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from inventory_manager import InventoryManager
from exceptions import ValidationError, NotFoundError

kunden_bp = Blueprint('kunden', __name__)
inventory = InventoryManager()

@kunden_bp.route('', methods=['GET'])
@jwt_required()
def get_kunden():
    kunden = inventory.kunden_auflisten()
    return jsonify([{
        'id': k.id,
        'name': k.name,
        'kontakt': k.kontakt
    } for k in kunden])

@kunden_bp.route('', methods=['POST'])
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

@kunden_bp.route('/<int:kunde_id>', methods=['GET'])
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