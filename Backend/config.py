import os
from dotenv import load_dotenv

load_dotenv()  # charge le fichier .env AVANT toute lecture de os.environ


def _require_env(key):
    
    value = os.environ.get(key)
    if not value:
        raise RuntimeError(
            f"Variable d'environnement '{key}' manquante. "
            f"Ajoute-la dans ton fichier .env avant de lancer l'application."
        )
    return value


class Config:
    SECRET_KEY     = _require_env("SECRET_KEY")
    JWT_SECRET_KEY = _require_env("JWT_SECRET_KEY")

    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES", 3600))

    ORACLE_USER     = _require_env("ORACLE_USER")
    ORACLE_PASSWORD = _require_env("ORACLE_PASSWORD")
    ORACLE_DSN      = os.environ.get("ORACLE_DSN", "localhost:1521/XE")

    SQLALCHEMY_DATABASE_URI = (
        f"oracle+oracledb://{ORACLE_USER}:{ORACLE_PASSWORD}@{ORACLE_DSN}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MODEL_PATH      = "app/services/fraud_model.pkl"
    THRESHOLD_FRAUD = float(os.environ.get("THRESHOLD_FRAUD", 0.7))

    # Identifiants admin — lus depuis .env, jamais en dur dans le code
    ADMIN_EMAIL         = os.environ.get("ADMIN_EMAIL", "")
    ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH", "")