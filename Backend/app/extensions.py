from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db      = SQLAlchemy()
jwt     = JWTManager()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],          # Pas de limite globale — on cible uniquement /login
    storage_uri="memory://"     # En production, remplacez par Redis: "redis://localhost:6379"
)
