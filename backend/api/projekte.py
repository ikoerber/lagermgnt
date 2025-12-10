from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from inventory_manager import InventoryManager
from reports import ReportGenerator
from exceptions import ValidationError, NotFoundError

projekte_bp = Blueprint('projekte', __name__)
inventory = InventoryManager()
reports = ReportGenerator()

@projekte_bp.route('', methods=['GET'])
@jwt_required()
def get_projekte():
    projekte = inventory.projekte_auflisten()
    return jsonify([{
        'id': p[0],
        'projektname': p[1],
        'kunde_name': p[2]
    } for p in projekte])

@projekte_bp.route('', methods=['POST'])
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

@projekte_bp.route('/<int:projekt_id>', methods=['GET'])
@jwt_required()
def get_projekt_detail(projekt_id):
    uebersicht = reports.projekt_uebersicht(projekt_id)
    if not uebersicht:
        raise NotFoundError('Projekt nicht gefunden')
    
    return jsonify(uebersicht)