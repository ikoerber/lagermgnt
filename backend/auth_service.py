from datetime import datetime, timedelta
from typing import Optional
from database import Database
from models import User
from logger_config import app_logger
from exceptions import ValidationError, NotFoundError, LagerverwaltungError
from flask_jwt_extended import create_access_token, create_refresh_token, get_jti


class AuthService:
    def __init__(self):
        self.db = Database()
        app_logger.info("AuthService initialisiert")
    
    # User Management
    def create_user(self, username: str, password: str) -> int:
        """Erstelle neuen User"""
        if not username or not username.strip():
            raise ValidationError("Username darf nicht leer sein")
        if not password or len(password) < 6:
            raise ValidationError("Passwort muss mindestens 6 Zeichen lang sein")
        
        username = username.strip().lower()
        app_logger.info(f"Erstelle User: {username}")
        
        # Prüfen ob Username bereits existiert
        existing_user = self.find_user_by_username(username)
        if existing_user:
            raise ValidationError(f"Username '{username}' existiert bereits")
        
        # Passwort hashen und User erstellen
        password_hash = User.hash_password(password)
        created_at = datetime.now().isoformat()
        
        try:
            query = "INSERT INTO users (username, password_hash, created_at, active) VALUES (?, ?, ?, ?)"
            user_id = self.db.execute_insert(query, (username, password_hash, created_at, True))
            app_logger.info(f"User '{username}' erfolgreich erstellt mit ID {user_id}")
            return user_id
        except Exception as e:
            app_logger.error(f"Fehler beim Erstellen von User '{username}': {e}")
            raise LagerverwaltungError(f"Fehler beim Erstellen des Users: {e}")
    
    def find_user_by_username(self, username: str) -> Optional[User]:
        """Finde User anhand Username"""
        if not username:
            return None
        
        username = username.strip().lower()
        try:
            query = "SELECT id, username, password_hash, created_at, active FROM users WHERE username = ? AND active = 1"
            results = self.db.execute_query(query, (username,))
            
            if results:
                row = results[0]
                return User(
                    id=row[0],
                    username=row[1], 
                    password_hash=row[2],
                    created_at=row[3],
                    active=bool(row[4])
                )
            return None
        except Exception as e:
            app_logger.error(f"Fehler beim Suchen von User '{username}': {e}")
            return None
    
    def find_user_by_id(self, user_id: int) -> Optional[User]:
        """Finde User anhand ID"""
        try:
            query = "SELECT id, username, password_hash, created_at, active FROM users WHERE id = ? AND active = 1"
            results = self.db.execute_query(query, (user_id,))
            
            if results:
                row = results[0]
                return User(
                    id=row[0],
                    username=row[1],
                    password_hash=row[2], 
                    created_at=row[3],
                    active=bool(row[4])
                )
            return None
        except Exception as e:
            app_logger.error(f"Fehler beim Suchen von User ID {user_id}: {e}")
            return None
    
    def list_users(self) -> list:
        """Liste alle aktiven User"""
        try:
            query = "SELECT id, username, created_at, active FROM users WHERE active = 1 ORDER BY username"
            results = self.db.execute_query(query)
            
            users = []
            for row in results:
                users.append({
                    'id': row[0],
                    'username': row[1],
                    'created_at': row[2],
                    'active': bool(row[3])
                })
            return users
        except Exception as e:
            app_logger.error(f"Fehler beim Auflisten der User: {e}")
            return []
    
    # Authentication
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authentifiziere User mit Username/Password"""
        if not username or not password:
            app_logger.warning("Login-Versuch mit leeren Credentials")
            return None
        
        user = self.find_user_by_username(username)
        if not user:
            app_logger.warning(f"Login-Versuch mit unbekanntem Username: {username}")
            return None
        
        if not user.check_password(password):
            app_logger.warning(f"Login-Versuch mit falschem Passwort für User: {username}")
            return None
        
        app_logger.info(f"Erfolgreiche Authentifizierung für User: {username}")
        return user
    
    def create_tokens(self, user: User) -> dict:
        """Erstelle JWT Access und Refresh Token für User"""
        try:
            # Zusätzliche Claims für den Token
            additional_claims = {
                'username': user.username,
                'user_id': user.id
            }
            
            # Access Token (1 Stunde gültig)
            access_token = create_access_token(
                identity=str(user.id),
                additional_claims=additional_claims,
                expires_delta=timedelta(hours=1)
            )
            
            # Refresh Token (7 Tage gültig)
            refresh_token = create_refresh_token(
                identity=str(user.id),
                additional_claims=additional_claims,
                expires_delta=timedelta(days=7)
            )
            
            app_logger.info(f"JWT Tokens erstellt für User: {user.username}")
            
            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': 'Bearer',
                'expires_in': 3600,  # 1 Stunde in Sekunden
                'user': user.to_dict()
            }
        except Exception as e:
            app_logger.error(f"Fehler beim Erstellen von Tokens für User {user.username}: {e}")
            raise LagerverwaltungError(f"Fehler beim Erstellen der Tokens: {e}")
    
    # Token Blacklisting
    def blacklist_token(self, jti: str):
        """Füge Token zur Blacklist hinzu (für Logout)"""
        try:
            created_at = datetime.now().isoformat()
            query = "INSERT OR IGNORE INTO blacklisted_tokens (jti, created_at) VALUES (?, ?)"
            self.db.execute_insert(query, (jti, created_at))
            app_logger.info(f"Token zur Blacklist hinzugefügt: {jti[:8]}...")
        except Exception as e:
            app_logger.error(f"Fehler beim Blacklisting von Token: {e}")
    
    def is_token_blacklisted(self, jti: str) -> bool:
        """Prüfe ob Token auf der Blacklist steht"""
        try:
            query = "SELECT COUNT(*) FROM blacklisted_tokens WHERE jti = ?"
            results = self.db.execute_query(query, (jti,))
            return results[0][0] > 0
        except Exception as e:
            app_logger.error(f"Fehler beim Prüfen der Token-Blacklist: {e}")
            return False
    
    def cleanup_blacklisted_tokens(self, days_old: int = 30):
        """Lösche alte Blacklist-Einträge (Cleanup-Job)"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days_old)).isoformat()
            query = "DELETE FROM blacklisted_tokens WHERE created_at < ?"
            self.db.execute_query(query, (cutoff_date,))
            app_logger.info(f"Alte Blacklist-Tokens (älter als {days_old} Tage) gelöscht")
        except Exception as e:
            app_logger.error(f"Fehler beim Cleanup der Blacklist: {e}")