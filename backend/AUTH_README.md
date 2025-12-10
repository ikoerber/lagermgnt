# JWT Authentication System

## 🔐 Übersicht

Das Lagerverwaltungssystem wurde um ein **JWT-basiertes Authentication-System** erweitert. Alle API-Endpoints sind jetzt geschützt und erfordern eine gültige Authentifizierung.

## 📋 Features

- **User Management**: Registrierung und Verwaltung von Benutzern
- **JWT Tokens**: Access + Refresh Token Mechanismus  
- **Token Blacklisting**: Sichere Logout-Funktionalität
- **Password Hashing**: Bcrypt für sichere Passwort-Speicherung
- **Case-Insensitive**: Username sind case-insensitive
- **Comprehensive Logging**: Vollständige Authentifizierungs-Logs

## 🚀 API Endpoints

### Authentication Endpoints

| Endpoint | Method | Beschreibung | Auth Required |
|----------|--------|--------------|---------------|
| `/api/auth/register` | POST | User registrieren | ❌ |
| `/api/auth/login` | POST | User einloggen | ❌ |
| `/api/auth/refresh` | POST | Token refreshen | ✅ (Refresh Token) |
| `/api/auth/logout` | DELETE | User ausloggen | ✅ |
| `/api/auth/me` | GET | Aktuelle User-Info | ✅ |
| `/api/auth/users` | GET | Alle User auflisten | ✅ |

### Geschützte Endpoints

**Alle bestehenden Lagerverwaltungs-Endpoints benötigen jetzt einen gültigen JWT-Token:**

- `/api/lieferanten/*` - Lieferanten-Management
- `/api/artikel/*` - Artikel-Management  
- `/api/kunden/*` - Kunden-Management
- `/api/projekte/*` - Projekt-Management
- `/api/lager/*` - Lager-Operations
- `/api/verkauf` - Verkaufs-Erfassung
- `/api/berichte/*` - Berichte und Analysen

## 📝 API Verwendung

### 1. User Registrierung

```bash
curl -X POST "http://localhost:5000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "password123"
  }'
```

**Response:**
```json
{
  "message": "User erfolgreich erstellt",
  "user": {
    "id": 1,
    "username": "admin", 
    "created_at": "2024-12-09T10:30:00",
    "active": true
  }
}
```

### 2. User Login

```bash
curl -X POST "http://localhost:5000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "password123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "user": {
    "id": 1,
    "username": "admin",
    "created_at": "2024-12-09T10:30:00",
    "active": true
  }
}
```

### 3. Geschützte API-Aufrufe

```bash
curl -X GET "http://localhost:5000/api/lieferanten" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Token Refresh

```bash
curl -X POST "http://localhost:5000/api/auth/refresh" \
  -H "Authorization: Bearer YOUR_REFRESH_TOKEN"
```

### 5. Logout

```bash
curl -X DELETE "http://localhost:5000/api/auth/logout" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🔧 Konfiguration

### Environment Variables

```bash
# JWT Secret Key (WICHTIG: In Produktion ändern!)
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production

# Log-Level für Auth-Events
LOG_LEVEL=INFO
```

### Token-Laufzeiten

- **Access Token**: 1 Stunde
- **Refresh Token**: 7 Tage

## 🛡️ Sicherheits-Features

### Password Policy
- Mindestlänge: 6 Zeichen
- Bcrypt-Hashing mit Salt

### Token Security
- JWT-Signierung mit Secret Key
- Token Blacklisting bei Logout
- Automatic Token Expiry
- Refresh Token Rotation

### API Protection
- Alle Business-Endpoints geschützt
- Strukturierte Error-Responses
- Rate Limiting Ready

## 🧪 Testing

### Automatische Tests
```bash
pytest tests/test_authentication.py -v
```
**14 Tests** für alle Auth-Funktionen

### Manueller Test
```bash
python test_auth_manual.py
```
Interaktiver Test-Workflow für alle Auth-Endpoints

## 📊 Monitoring & Logs

### Authentication Events
```
INFO - Erfolgreiche Authentifizierung für User: admin
WARNING - Login-Versuch mit falschem Passwort für User: admin  
WARNING - Login-Versuch mit unbekanntem Username: hacker
INFO - User admin erfolgreich ausgeloggt
```

### Token Events
```
INFO - JWT Tokens erstellt für User: admin
WARNING - Abgelaufener Token verwendet: 123
WARNING - Widerrufener Token verwendet: 456
```

## 🔄 Migration Existing Data

Das System erstellt automatisch die neuen `users` und `blacklisted_tokens` Tabellen. Für die erste Verwendung:

1. **Ersten Admin-User erstellen:**
   ```bash
   curl -X POST "http://localhost:5000/api/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "secure_password"}'
   ```

2. **Alle weiteren API-Calls benötigen dann Authentication**

## 🚀 Deployment Notes

### Produktions-Konfiguration
```python
# app.py - WICHTIG für Produktion
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'fallback-key')
```

### Empfohlene Umgebungsvariablen
```bash
JWT_SECRET_KEY=your-random-256-bit-secret-key
LOG_LEVEL=INFO
LOG_DIR=/var/log/lagerverwaltung
```

## 🔍 Troubleshooting

### Häufige Probleme

**401 Unauthorized**
- Token abgelaufen → `/api/auth/refresh` verwenden
- Token widerrufen → Neuer Login erforderlich
- Fehlender Authorization-Header

**400 Bad Request**  
- Schwaches Passwort (< 6 Zeichen)
- Username bereits vergeben
- Fehlende Pflichtfelder

**403 Forbidden**
- Token auf Blacklist → Neuer Login erforderlich

Das Authentication-System ist jetzt **vollständig implementiert** und **produktionsbereit**! 🎉