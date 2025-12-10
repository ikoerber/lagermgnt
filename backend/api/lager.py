from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime
from inventory_manager import InventoryManager
from exceptions import ValidationError, NotFoundError

lager_bp = Blueprint('lager', __name__)
inventory = InventoryManager()

@lager_bp.route('/eingang', methods=['POST'])
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

@lager_bp.route('/bestand', methods=['GET'])
@jwt_required()
def get_lagerbestand():
    bestand = inventory.gesamter_lagerbestand()
    return jsonify([{
        'artikelnummer': b[0],
        'bezeichnung': b[1],
        'gesamtmenge': b[2],
        'durchschnittspreis': b[3]
    } for b in bestand])

@lager_bp.route('/bestand/<artikelnummer>', methods=['GET'])
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