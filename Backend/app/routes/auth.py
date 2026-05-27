from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash, generate_password_hash
from app.extensions import db
from app.models import Client

auth_bp = Blueprint("auth", __name__)

ADMIN_CREDENTIALS = {
    "yasmine@bank.com": "yasmine123"
}

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No data provided"}), 400

    email    = data.get("email", "").strip()
    password = data.get("password", "").strip()

    if not email or not password:
        return jsonify({"message": "Email et mot de passe requis"}), 400

    if email in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[email] == password:
        token = create_access_token(identity="admin")
        return jsonify({
            "message": "Login successful", "token": token,
            "role": "admin", "client_id": 0,
            "nom": "Admin", "prenom": "Banquier"
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
            pwd_ok = (password == raw) or (password in raw)

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
def reset_password():
    data   = request.get_json()
    email  = data.get("email")
    newpwd = data.get("new_password")
    client = Client.query.filter_by(email=email).first()
    if not client:
        return jsonify({"message": "Client introuvable"}), 404
    client.mot_de_passe = generate_password_hash(newpwd)
    db.session.commit()
    return jsonify({"message": "Mot de passe mis à jour"})