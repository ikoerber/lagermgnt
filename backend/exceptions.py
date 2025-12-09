class LagerverwaltungError(Exception):
    """Basis-Exception für Lagerverwaltung"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class LieferantError(LagerverwaltungError):
    """Fehler bei Lieferanten-Operationen"""
    pass

class ArtikelError(LagerverwaltungError):
    """Fehler bei Artikel-Operationen"""
    pass

class LagerError(LagerverwaltungError):
    """Fehler bei Lager-Operationen"""
    pass

class VerkaufError(LagerverwaltungError):
    """Fehler bei Verkaufs-Operationen"""
    pass

class ValidationError(LagerverwaltungError):
    """Validierungsfehler"""
    pass

class DatabaseError(LagerverwaltungError):
    """Datenbankfehler"""
    pass

class NotFoundError(LagerverwaltungError):
    """Ressource nicht gefunden"""
    pass

class IntegrityError(LagerverwaltungError):
    """Referentielle Integrität verletzt"""
    pass