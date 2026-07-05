from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from app.extensions import db
from app.models import Client

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No data provided"}), 400

    email    = data.get("email", "").strip()
    password = data.get("password", "").strip()

    if not email or not password:
        return jsonify({"message": "Email et mot de passe requis"}), 400

    # CORRECTION : identifiants admin lus depuis .env (config.py), plus en dur
    admin_email = current_app.config.get("ADMIN_EMAIL", "")
    admin_hash  = current_app.config.get("ADMIN_PASSWORD_HASH", "")

    if admin_email and email == admin_email and admin_hash and check_password_hash(admin_hash, password):
        token = create_access_token(identity="admin")
        return jsonify({
            "message": "Login successful", "token": token,
            "role": "yasmine", "client_id": 0,
            "nom": "Yasmine", "prenom": "Banquier"
        }), 200

    try:
        client = Client.query.filter_by(email=email).first()
        if not client:
            return jsonify({"message": "Identifiants incorrects"}), 401

        pwd_ok = False
        raw = client.mot_de_passe or ""
        if raw.startswith("$2b$") and len(raw) == 60:
            pwd_ok = check_password_hash(raw, password)
        else:
            pwd_ok = (password == raw)  # CORRECTION : suppression du "in raw" (faille de comparaison partielle)

        if not pwd_ok:
            return jsonify({"message": "Identifiants incorrects"}), 401

        if client.statut != "ACTIF":
            return jsonify({"message": "Compte suspendu ou clôturé"}), 403

        token = create_access_token(identity=str(client.client_id))
        return jsonify({
            "message": "Login successful", "token": token,
            "role": "banquier", "client_id": client.client_id,
            "nom": client.nom, "prenom": client.prenom
        }), 200

    except Exception as e:
        return jsonify({"message": f"Erreur base de données : {str(e)}"}), 500


@auth_bp.route("/api/reset-password", methods=["POST"])
@jwt_required()
def reset_password():
    """
    CORRECTION : route désormais protégée par JWT.
    - L'admin ("yasmine") peut réinitialiser le mot de passe de n'importe quel client.
    - Un client ne peut réinitialiser QUE son propre mot de passe.
    """
    current_identity = get_jwt_identity()

    data   = request.get_json() or {}
    email  = data.get("email")
    newpwd = data.get("new_password")

    if not email or not newpwd:
        return jsonify({"message": "Email et nouveau mot de passe requis"}), 400

    client = Client.query.filter_by(email=email).first()
    if not client:
        return jsonify({"message": "Client introuvable"}), 404

    is_admin      = (current_identity == "admin")
    is_self_reset = (current_identity == str(client.client_id))

    if not (is_admin or is_self_reset):
        return jsonify({"message": "Non autorisé"}), 403

    client.mot_de_passe = generate_password_hash(newpwd)
    db.session.commit()
    return jsonify({"message": "Mot de passe mis à jour"})