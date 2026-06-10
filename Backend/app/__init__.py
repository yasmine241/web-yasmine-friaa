from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from app.extensions import db, jwt, limiter


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ── CORS — origines lues depuis la config (plus de "null" autorisé) ─────────
    CORS(
        app,
        origins=app.config["ALLOWED_ORIGINS"],
        supports_credentials=True
    )

    # ── Extensions ──────────────────────────────────────────────────────────────
    db.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)

    # ── Gestion globale des erreurs JWT ─────────────────────────────────────────
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"message": "Session expirée, veuillez vous reconnecter."}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"message": "Token invalide."}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({"message": "Authentification requise."}), 401

    # ── Blueprints ──────────────────────────────────────────────────────────────
    from app.routes.auth         import auth_bp
    from app.routes.clients      import clients_bp
    from app.routes.comptes      import comptes_bp
    from app.routes.transactions import transactions_bp
    from app.routes.dashboard    import dashboard_bp
    from app.routes.fraud        import fraud_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(comptes_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(fraud_bp)

    @app.route("/")
    def home():
        return jsonify({"message": "API SG SecureBank running ✅", "version": "1.0"})

    return app
