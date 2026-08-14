from flask import Flask, request, g
from flask_cors import CORS
from config import Config
from app.extensions import db, jwt
import logging
import time

# Logger dédié aux mesures de performance 
perf_logger = logging.getLogger("sgsecurebank.perf")
perf_logger.setLevel(logging.INFO)
if not perf_logger.handlers:
    _handler = logging.FileHandler("performance.log", encoding="utf-8")
    _handler.setFormatter(logging.Formatter("%(asctime)s | %(message)s"))
    perf_logger.addHandler(_handler)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # CORS appliqué EN PREMIER
    CORS(app,
         origins=["http://localhost:8080", "http://127.0.0.1:8080", "null"],
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

    # Header CORS de secours sur TOUTES les réponses 
    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"]  = "http://localhost:8080"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        return response

    @app.before_request
    def _start_timer():
        g._start_time = time.perf_counter()

    @app.after_request
    def _log_response_time(response):
        if hasattr(g, "_start_time"):
            elapsed_ms = (time.perf_counter() - g._start_time) * 1000
            response.headers["X-Response-Time-ms"] = f"{elapsed_ms:.1f}"
            perf_logger.info(
                f"{request.method} {request.path} -> {response.status_code} "
                f"in {elapsed_ms:.1f} ms"
            )
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