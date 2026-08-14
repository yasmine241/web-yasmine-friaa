from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models import Transaction, Fraud
from app.services.fraud_detector import FraudDetector
from datetime import datetime, timezone

transactions_bp = Blueprint("transactions", __name__)
detector        = FraudDetector()


def _normalize_score(score):
    """
    Normalise le score_risque en valeur entre 0 et 1.
    Corrige les anciennes valeurs aberrantes stockées en base.
    """
    score = float(score or 0)
    if score > 100:
        score = score / 10000   # ex: 9013 → 0.9013
    elif score > 1:
        score = score / 100     # ex: 90.13 → 0.9013
    return round(min(max(score, 0.0), 1.0), 4)


@transactions_bp.route("/api/transactions", methods=["GET"])
@jwt_required()
def get_transactions():
    page     = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 50, type=int), 200)  # plafond anti-abus
    pagination = Transaction.query.order_by(Transaction.date_transaction.desc()) \
                                   .paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "items":       [_fmt(t) for t in pagination.items],
        "page":        pagination.page,
        "per_page":    per_page,
        "total":       pagination.total,
        "total_pages": pagination.pages
    })


@transactions_bp.route("/api/transactions/<int:id>", methods=["GET"])
@jwt_required()
def get_transaction(id):
    t = db.session.get(Transaction, id)
    if not t:
        return jsonify({"message": "Transaction not found"}), 404
    return jsonify(_fmt(t))


@transactions_bp.route("/api/transactions", methods=["POST"])
@jwt_required()
def create_transaction():
    data = request.get_json() or {}
    required = ["compte_id", "montant", "type_transaction"]
    for field in required:
        if data.get(field) in (None, ""):
            return jsonify({"message": f"Champ requis manquant : {field}"}), 400
    try:
        montant = float(data["montant"])
    except (TypeError, ValueError):
        return jsonify({"message": "Le champ montant doit être numérique"}), 400
    if montant <= 0:
        return jsonify({"message": "Le montant doit être strictement positif"}), 400

    result = detector.predict({
        "montant":          montant,
        "pays_origine":     data.get("pays_origine",     "France"),
        "pays_destination": data.get("pays_destination", "France"),
        "type_transaction": data.get("type_transaction", "VIREMENT")
    })

    # CORRECTION : score ML est entre 0 et 1 — on le stocke tel quel (pas × 100)
    score    = float(result["score"])
    score    = round(min(max(score, 0.0), 1.0), 4)   # sécurité : clamp 0-1
    is_fraud = result["fraud"]
    status   = "EN_ANALYSE" if is_fraud else "VALIDEE"

    # Vérification explicite que le compte existe AVANT d'insérer,
    # pour éviter un crash brut (violation de contrainte FK) qui,
    # en mode debug, casse la réponse et fait croire à une erreur CORS.
    from app.models import Compte
    compte = db.session.get(Compte, data["compte_id"])
    if compte is None:
        return jsonify({
            "message": f"Aucun compte trouvé avec l'ID {data['compte_id']}. "
                       f"Utilise l'ID interne du compte (compte_id), pas le numéro de compte / IBAN."
        }), 404

    new_tx = Transaction(
        compte_id        = data["compte_id"],
        type_transaction = data["type_transaction"],
        montant          = montant,
        devise           = data.get("devise", "EUR"),
        pays_origine     = data.get("pays_origine",     "France"),
        pays_destination = data.get("pays_destination", "France"),
        date_transaction = datetime.now(timezone.utc),
        ip_adresse       = request.remote_addr,
        statut           = status,
        score_risque     = score   # CORRECTION : stocké en 0-1 (ex: 0.9013)
    )

    try:
        db.session.add(new_tx)
        db.session.commit()

        if is_fraud:
            niveau = "CRITIQUE" if score >= 0.9 else "ELEVE"
            db.session.add(Fraud(
                transaction_id = new_tx.transaction_id,
                type_fraude    = "TRANSACTION_INHABITUELLE",
                niveau_risque  = niveau,
                score_ml       = score,   # CORRECTION : stocké en 0-1
                date_detection = datetime.now(timezone.utc),
                statut_analyse = "EN_COURS"
            ))
            db.session.commit()
    except Exception as e:
        # Toute erreur DB (contrainte, type invalide, connexion...) est
        # désormais interceptée et renvoyée en JSON propre au lieu de
        # crasher le serveur (ce qui coupait la réponse et déclenchait
        # une fausse erreur CORS côté navigateur).
        db.session.rollback()
        return jsonify({"message": f"Erreur lors de la création de la transaction : {str(e)}"}), 500

    return jsonify({
        "message":      "Transaction créée",
        "id":           new_tx.transaction_id,
        "score_risque": score,   # CORRECTION : renvoyé en 0-1 au frontend
        "fraud":        is_fraud,
        "statut":       status
    }), 201


def _fmt(t):
    return {
        "id":               t.transaction_id,
        "compte_id":        t.compte_id,
        "type":             t.type_transaction,
        "montant":          t.montant,
        "devise":           t.devise,
        "pays_origine":     t.pays_origine,
        "pays_destination": t.pays_destination,
        "statut":           t.statut,
        "score_risque":     _normalize_score(t.score_risque),  # CORRECTION : toujours 0-1
        "date_transaction": str(t.date_transaction)
    }