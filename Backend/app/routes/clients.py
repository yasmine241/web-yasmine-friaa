from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from werkzeug.security import generate_password_hash
from app.extensions import db
from app.models import Client
from datetime import datetime

clients_bp = Blueprint("clients", __name__)

@clients_bp.route("/api/clients", methods=["POST"])
@jwt_required()
def create_client():
    data = request.get_json()
    required = ["nom", "prenom", "email", "mot_de_passe", "date_naissance"]
    for field in required:
        if not data.get(field):
            return jsonify({"message": f"Champ requis manquant : {field}"}), 400

    if Client.query.filter_by(email=data["email"]).first():
        return jsonify({"message": "Cet email est déjà utilisé"}), 409

    try:
        date_naissance = datetime.strptime(data["date_naissance"], "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"message": "Format date invalide, attendu : YYYY-MM-DD"}), 400

    new_client = Client(
        nom            = data["nom"],
        prenom         = data["prenom"],
        email          = data["email"],
        mot_de_passe   = generate_password_hash(data["mot_de_passe"]),
        telephone      = data.get("telephone"),
        date_naissance = date_naissance,
        adresse        = data.get("adresse"),
        pays           = data.get("pays", "France"),
        statut         = "ACTIF"
    )
    db.session.add(new_client)
    db.session.commit()
    return jsonify({"message": "Client créé avec succès", "client_id": new_client.client_id}), 201

@clients_bp.route("/api/clients", methods=["GET"])
@jwt_required()
def get_clients():
    clients = Client.query.all()
    return jsonify([_fmt(c) for c in clients])

@clients_bp.route("/api/clients/<int:id>", methods=["GET"])
@jwt_required()
def get_client(id):
    c = Client.query.get(id)
    if not c:
        return jsonify({"message": "Client introuvable"}), 404
    return jsonify({**_fmt(c), "telephone": c.telephone, "adresse": c.adresse})

@clients_bp.route("/api/clients/<int:id>", methods=["PUT"])
@jwt_required()
def update_client(id):
    c = Client.query.get(id)
    if not c:
        return jsonify({"message": "Client introuvable"}), 404
    data = request.get_json()
    c.nom       = data.get("nom",       c.nom)
    c.prenom    = data.get("prenom",    c.prenom)
    c.telephone = data.get("telephone", c.telephone)
    c.adresse   = data.get("adresse",   c.adresse)
    c.pays      = data.get("pays",      c.pays)
    c.statut    = data.get("statut",    c.statut)
    if data.get("mot_de_passe"):
        c.mot_de_passe = generate_password_hash(data["mot_de_passe"])
    db.session.commit()
    return jsonify({"message": "Client mis à jour"})

@clients_bp.route("/api/clients/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_client(id):
    c = Client.query.get(id)
    if not c:
        return jsonify({"message": "Client introuvable"}), 404
    db.session.delete(c)
    db.session.commit()
    return jsonify({"message": "Client supprimé"})

def _fmt(c):
    return {
        "id": c.client_id, "nom": c.nom, "prenom": c.prenom,
        "email": c.email, "pays": c.pays, "statut": c.statut
    }