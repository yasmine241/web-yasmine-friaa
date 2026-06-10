import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "sg_securebank_super_secret_key_2024_XYZ!")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "sg_securebank_jwt_super_secret_key_2024_XYZ!")
    JWT_ACCESS_TOKEN_EXPIRES = False

    ORACLE_USER     = os.environ.get("ORACLE_USER",     "system")
    ORACLE_PASSWORD = os.environ.get("ORACLE_PASSWORD", "2002")
    ORACLE_DSN      = os.environ.get("ORACLE_DSN",      "localhost:1521/XE")

    SQLALCHEMY_DATABASE_URI = (
        f"oracle+oracledb://{os.environ.get('ORACLE_USER','system')}:"
        f"{os.environ.get('ORACLE_PASSWORD','2002')}@"
        f"{os.environ.get('ORACLE_DSN','localhost:1521/XE')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MODEL_PATH      = "app/services/fraud_model.pkl"
    THRESHOLD_FRAUD = 0.7