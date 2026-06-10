from flask import Flask
from flask_cors import CORS
from config import Config
from app.extensions import db, jwt


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # CORS appliqué EN PREMIER
    CORS(app,
         origins=["http://localhost:8080", "http://127.0.0.1:8080", "null"],
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

    # Header CORS de secours sur TOUTES les réponses (y compris erreurs 500)
    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"]  = "http://localhost:8080"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        return response

    db.init_app(app)
    jwt.init_app(app)

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
        return {"message": "API SG SecureBank running ✅"}

    return app