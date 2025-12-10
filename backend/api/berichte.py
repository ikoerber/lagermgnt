from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from inventory_manager import InventoryManager
from reports import ReportGenerator

berichte_bp = Blueprint('berichte', __name__)
inventory = InventoryManager()
reports = ReportGenerator()

@berichte_bp.route('/lagerbestand', methods=['GET'])
@jwt_required()
def get_lagerbestand_detailliert():
    detailliert = request.args.get('detailliert', 'false').lower() == 'true'
    
    if detailliert:
        bestand = reports.lagerbestand_detailliert()
    else:
        bestand = reports.lagerbestand_zusammenfassung()
    
    return jsonify(bestand)

@berichte_bp.route('/projekte', methods=['GET'])
@jwt_required()
def get_alle_projekte_bericht():
    projekte = reports.alle_projekte_uebersicht()
    return jsonify(projekte)

@berichte_bp.route('/gewinn', methods=['GET'])
@jwt_required()
def get_gewinn_analyse():
    projekt_id = request.args.get('projekt_id', type=int)
    analyse = reports.gewinn_analyse(projekt_id)
    return jsonify(analyse)

@berichte_bp.route('/lagerumschlag', methods=['GET'])
@jwt_required()
def get_lagerumschlag():
    umschlag = reports.lagerumschlag()
    return jsonify(umschlag)

@berichte_bp.route('/mindestmenge', methods=['GET'])
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