from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime
from inventory_manager import InventoryManager
from exceptions import ValidationError, NotFoundError, LagerError

verkauf_bp = Blueprint('verkauf', __name__)
inventory = InventoryManager()

@verkauf_bp.route('', methods=['POST'])
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