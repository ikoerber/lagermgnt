from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from inventory_manager import InventoryManager
from logger_config import app_logger
from exceptions import ValidationError, NotFoundError

artikel_bp = Blueprint('artikel', __name__)
inventory = InventoryManager()

@artikel_bp.route('', methods=['GET'])
@jwt_required()
def get_artikel():
    artikel = inventory.artikel_auflisten()
    return jsonify([{
        'artikelnummer': a[0],
        'bezeichnung': a[1],
        'lieferant_name': a[2],
        'mindestmenge': a[3]
    } for a in artikel])

@artikel_bp.route('', methods=['POST'])
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

@artikel_bp.route('/<artikelnummer>', methods=['GET'])
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