import os
from dotenv import load_dotenv

load_dotenv()  # charge le fichier .env AVANT toute lecture de os.environ

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "sg_securebank_super_secret_key_2024_XYZ!")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "sg_securebank_jwt_super_secret_key_2024_XYZ!")

    # CORRECTION : lit la durée depuis .env (en secondes). Fallback = 1h.
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES", 3600))

    ORACLE_USER     = os.environ.get("ORACLE_USER",     "system")
    ORACLE_PASSWORD = os.environ.get("ORACLE_PASSWORD", "2002")
    ORACLE_DSN      = os.environ.get("ORACLE_DSN",      "localhost:1521/XE")

    SQLALCHEMY_DATABASE_URI = (
        f"oracle+oracledb://{ORACLE_USER}:{ORACLE_PASSWORD}@{ORACLE_DSN}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MODEL_PATH      = "app/services/fraud_model.pkl"
    THRESHOLD_FRAUD = float(os.environ.get("THRESHOLD_FRAUD", 0.7))

    # Identifiants admin — lus depuis .env, plus jamais en dur dans le code
    ADMIN_EMAIL         = os.environ.get("ADMIN_EMAIL", "")
    ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH", "")