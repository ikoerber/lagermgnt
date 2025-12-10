from flask import Flask
from .auth import auth_bp
from .lieferanten import lieferanten_bp
from .artikel import artikel_bp
from .kunden import kunden_bp
from .projekte import projekte_bp
from .lager import lager_bp
from .verkauf import verkauf_bp
from .berichte import berichte_bp

def register_blueprints(app: Flask):
    """Registriert alle API-Blueprints mit der Flask-App"""
    
    # Auth API
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    # Main Entity APIs
    app.register_blueprint(lieferanten_bp, url_prefix='/api/lieferanten')
    app.register_blueprint(artikel_bp, url_prefix='/api/artikel')
    app.register_blueprint(kunden_bp, url_prefix='/api/kunden')
    app.register_blueprint(projekte_bp, url_prefix='/api/projekte')
    
    # Operational APIs
    app.register_blueprint(lager_bp, url_prefix='/api/lager')
    app.register_blueprint(verkauf_bp, url_prefix='/api/verkauf')
    app.register_blueprint(berichte_bp, url_prefix='/api/berichte')