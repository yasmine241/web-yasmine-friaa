from flask import Flask
from flask_cors import CORS
from config import Config
from app.extensions import db, jwt


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    # ✅ CORS — autorise le frontend local
    CORS(app, origins=["http://localhost:8080", "http://127.0.0.1:8080", "null"],
         supports_credentials=True)

    db.init_app(app)
    jwt.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.clients import clients_bp
    from app.routes.comptes import comptes_bp
    from app.routes.transactions import transactions_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.fraud import fraud_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(comptes_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(fraud_bp)

    @app.route("/")
    def home():
        return {"message": "API SG SecureBank running ✅"}

    return app