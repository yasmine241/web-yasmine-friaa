from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from werkzeug.security import generate_password_hash
from app.extensions import db
from app.models import Client
from datetime import datetime
import re

clients_bp = Blueprint("clients", __name__)

# ── Helpers ──────────────────────────────────────────────────────────────────

def _error(message: str, status: int):
    return jsonify({"success": False, "message": message}), status

def _fmt(c: Client) -> dict:
    return {
        "id":            c.client_id,
        "nom":           c.nom,
        "prenom":        c.prenom,
        "email":         c.email,
        "telephone":     c.telephone,
        "pays":          c.pays,
        "statut":        c.statut,
        "date_creation": str(c.date_creation) if c.date_creation else None,
    }

def _validate_email(email: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))


# ── POST /api/clients ────────────────────────────────────────────────────────
@clients_bp.route("/api/clients", methods=["POST"])
@jwt_required()
def create_client():
    data = request.get_json(silent=True) or {}
    required = ["nom", "prenom", "email", "mot_de_passe", "date_naissance"]
    for field in required:
        if not data.get(field):
            return _error(f"Champ requis manquant : {field}.", 400)

    email = data["email"].strip().lower()
    if not _validate_email(email):
        return _error("Format d'email invalide.", 400)

    if len(data.get("mot_de_passe", "")) < 8:
        return _error("Le mot de passe doit contenir au moins 8 caractères.", 400)

    if Client.query.filter_by(email=email).first():
        return _error("Cet email est déjà utilisé.", 409)

    try:
        date_naissance = datetime.strptime(data["date_naissance"], "%Y-%m-%d").date()
    except ValueError:
        return _error("Format de date invalide. Attendu : YYYY-MM-DD.", 400)

    new_client = Client(
        nom            = data["nom"].strip(),
        prenom         = data["prenom"].strip(),
        email          = email,
        mot_de_passe   = generate_password_hash(data["mot_de_passe"]),
        telephone      = data.get("telephone", "").strip() or None,
        date_naissance = date_naissance,
        adresse        = data.get("adresse", "").strip() or None,
        pays           = data.get("pays", "France").strip(),
        date_creation  = datetime.utcnow(),
        statut         = "ACTIF",
    )
    db.session.add(new_client)
    db.session.commit()
    return jsonify({
        "success":   True,
        "message":   "Client créé avec succès.",
        "client_id": new_client.client_id
    }), 201


# ── GET /api/clients ─────────────────────────────────────────────────────────
@clients_bp.route("/api/clients", methods=["GET"])
@jwt_required()
def get_clients():
    # Filtres optionnels
    statut  = request.args.get("statut")
    pays    = request.args.get("pays")
    search  = request.args.get("q", "").strip()

    query = Client.query
    if statut:
        query = query.filter_by(statut=statut.upper())
    if pays:
        query = query.filter_by(pays=pays)
    if search:
        like = f"%{search}%"
        query = query.filter(
            db.or_(
                Client.nom.ilike(like),
                Client.prenom.ilike(like),
                Client.email.ilike(like)
            )
        )

    clients = query.order_by(Client.client_id.desc()).all()
    return jsonify([_fmt(c) for c in clients])


# ── GET /api/clients/<id> ────────────────────────────────────────────────────
@clients_bp.route("/api/clients/<int:id>", methods=["GET"])
@jwt_required()
def get_client(id):
    c = Client.query.get(id)
    if not c:
        return _error("Client introuvable.", 404)
    detail = _fmt(c)
    detail["adresse"] = c.adresse
    detail["date_naissance"] = str(c.date_naissance) if c.date_naissance else None
    return jsonify(detail)


# ── PUT /api/clients/<id> ────────────────────────────────────────────────────
@clients_bp.route("/api/clients/<int:id>", methods=["PUT"])
@jwt_required()
def update_client(id):
    c = Client.query.get(id)
    if not c:
        return _error("Client introuvable.", 404)

    data = request.get_json(silent=True) or {}
    c.nom       = data.get("nom",       c.nom)
    c.prenom    = data.get("prenom",    c.prenom)
    c.telephone = data.get("telephone", c.telephone)
    c.adresse   = data.get("adresse",   c.adresse)
    c.pays      = data.get("pays",      c.pays)
    c.statut    = data.get("statut",    c.statut)

    if data.get("mot_de_passe"):
        if len(data["mot_de_passe"]) < 8:
            return _error("Le mot de passe doit contenir au moins 8 caractères.", 400)
        c.mot_de_passe = generate_password_hash(data["mot_de_passe"])

    db.session.commit()
    return jsonify({"success": True, "message": "Client mis à jour avec succès."})


# ── DELETE /api/clients/<id> ─────────────────────────────────────────────────
@clients_bp.route("/api/clients/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_client(id):
    c = Client.query.get(id)
    if not c:
        return _error("Client introuvable.", 404)
    db.session.delete(c)
    db.session.commit()
    return jsonify({"success": True, "message": "Client supprimé avec succès."})
