from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models import Compte

comptes_bp = Blueprint("comptes", __name__)

@comptes_bp.route("/api/comptes", methods=["GET"])
@jwt_required()
def get_comptes():
    page     = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 50, type=int), 200)
    pagination = Compte.query.order_by(Compte.compte_id).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "items": [_fmt(c) for c in pagination.items],
        "page": pagination.page, "per_page": per_page,
        "total": pagination.total, "total_pages": pagination.pages
    })

@comptes_bp.route("/api/comptes/<int:id>", methods=["GET"])
@jwt_required()
def get_compte(id):
    c = Compte.query.get(id)
    if not c:
        return jsonify({"message": "Compte not found"}), 404
    return jsonify({**_fmt(c), "date_ouverture": str(c.date_ouverture)})

@comptes_bp.route("/api/comptes/client/<int:client_id>", methods=["GET"])
@jwt_required()
def get_comptes_by_client(client_id):
    return jsonify([_fmt(c) for c in Compte.query.filter_by(client_id=client_id).all()])

@comptes_bp.route("/api/comptes", methods=["POST"])
@jwt_required()
def create_compte():
    data = request.get_json() or {}
    required = ["client_id", "numero_compte"]
    for field in required:
        if not data.get(field):
            return jsonify({"message": f"Champ requis manquant : {field}"}), 400

    new_compte = Compte(
        client_id     = data["client_id"],
        numero_compte = data["numero_compte"],
        type_compte   = data.get("type_compte", "COURANT"),
        solde         = data.get("solde", 0.0),
        devise        = data.get("devise", "EUR"),
        statut        = data.get("statut", "ACTIF")
    )
    db.session.add(new_compte)
    db.session.commit()
    return jsonify({"message": "Compte créé", "id": new_compte.compte_id}), 201

@comptes_bp.route("/api/comptes/<int:id>", methods=["PUT"])
@jwt_required()
def update_compte(id):
    c = Compte.query.get(id)
    if not c:
        return jsonify({"message": "Compte not found"}), 404
    data = request.get_json()
    c.solde  = data.get("solde",  c.solde)
    c.statut = data.get("statut", c.statut)
    c.devise = data.get("devise", c.devise)
    db.session.commit()
    return jsonify({"message": "Compte mis à jour"})

@comptes_bp.route("/api/comptes/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_compte(id):
    c = Compte.query.get(id)
    if not c:
        return jsonify({"message": "Compte not found"}), 404
    db.session.delete(c)
    db.session.commit()
    return jsonify({"message": "Compte supprimé"})

def _fmt(c):
    return {
        "id": c.compte_id, "client_id": c.client_id,
        "numero_compte": c.numero_compte, "type_compte": c.type_compte,
        "solde": c.solde, "devise": c.devise, "statut": c.statut
    }