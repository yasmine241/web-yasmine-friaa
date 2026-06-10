import os
from datetime import timedelta
from dotenv import load_dotenv

# Charge .env si présent (développement local)
load_dotenv()


class Config:
    # ── Sécurité Flask ──────────────────────────────────────────────────────────
    SECRET_KEY = os.environ.get("SECRET_KEY")
    if not SECRET_KEY:
        raise RuntimeError(
            "SECRET_KEY est manquant. Définissez-la dans votre fichier .env "
            "ou via une variable d'environnement."
        )

    # ── JWT ─────────────────────────────────────────────────────────────────────
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    if not JWT_SECRET_KEY:
        raise RuntimeError(
            "JWT_SECRET_KEY est manquant. Définissez-la dans votre fichier .env."
        )

    # Expiration des tokens : 1 heure par défaut, configurable via .env
    _expires_seconds = int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES", 3600))
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=_expires_seconds)

    # ── Base de données Oracle ───────────────────────────────────────────────────
    ORACLE_USER     = os.environ.get("ORACLE_USER",     "system")
    ORACLE_PASSWORD = os.environ.get("ORACLE_PASSWORD", "2002")
    ORACLE_DSN      = os.environ.get("ORACLE_DSN",      "localhost:1521/XE")

    SQLALCHEMY_DATABASE_URI = (
        f"oracle+oracledb://{ORACLE_USER}:{ORACLE_PASSWORD}@{ORACLE_DSN}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── ML ──────────────────────────────────────────────────────────────────────
    MODEL_PATH      = os.environ.get("MODEL_PATH", "app/services/fraud_model.pkl")
    THRESHOLD_FRAUD = float(os.environ.get("THRESHOLD_FRAUD", 0.7))

    # ── CORS ────────────────────────────────────────────────────────────────────
    _origins_raw = os.environ.get(
        "ALLOWED_ORIGINS",
        "http://localhost:8080,http://127.0.0.1:8080"
    )
    ALLOWED_ORIGINS = [o.strip() for o in _origins_raw.split(",") if o.strip()]
