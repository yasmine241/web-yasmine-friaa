from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models import Fraud, Transaction, Compte
from app.services.fraud_detector import FraudDetector
from datetime import datetime

fraud_bp  = Blueprint("fraud", __name__)
detector  = FraudDetector()

# statut_analyse Oracle : EN_COURS | CONFIRME | FAUX_POSITIF | RESOLU
PENDING_STATUS = "EN_COURS"


# ======================
# POST /api/fraud/detect
# ======================
@fraud_bp.route("/api/fraud/detect", methods=["POST"])
@jwt_required()
def detect_fraud():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No data provided"}), 400

    result   = detector.predict(data)
    is_fraud = result["fraud"]
    score    = result["score"]

    niveau = "FAIBLE"
    if score >= 0.9:   niveau = "CRITIQUE"
    elif score >= 0.7: niveau = "ELEVE"
    elif score >= 0.5: niveau = "MOYEN"

    return jsonify({
        "is_fraud": is_fraud,
        "score":    score,
        "niveau":   niveau,
        "message":  "Fraude détectée" if is_fraud else "Transaction sûre"
    }), 200


# ======================
# GET /api/fraud/pending
# ======================
@fraud_bp.route("/api/fraud/pending", methods=["GET"])
@jwt_required()
def get_pending_frauds():
    frauds = Fraud.query.filter_by(statut_analyse=PENDING_STATUS)\
                        .order_by(Fraud.date_detection.desc()).all()
    return jsonify([_fmt_full(f) for f in frauds])


# ======================
# GET /api/fraud
# ======================
@fraud_bp.route("/api/fraud", methods=["GET"])
@jwt_required()
def get_frauds():
    page     = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 50, type=int), 200)
    pagination = Fraud.query.order_by(Fraud.date_detection.desc()) \
                             .paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "items": [_fmt_full(f) for f in pagination.items],
        "page": pagination.page, "per_page": per_page,
        "total": pagination.total, "total_pages": pagination.pages
    })


# ======================
# GET /api/fraud/<id>
# ======================
@fraud_bp.route("/api/fraud/<int:id>", methods=["GET"])
@jwt_required()
def get_fraud(id):
    f = Fraud.query.get(id)
    if not f:
        return jsonify({"message": "Fraud record not found"}), 404
    return jsonify(_fmt_full(f))


# ======================
# PUT /api/fraud/<id>/valider  → CONFIRME
# ======================
@fraud_bp.route("/api/fraud/<int:id>/valider", methods=["PUT"])
@jwt_required()
def valider_fraud(id):
    f = Fraud.query.get(id)
    if not f:
        return jsonify({"message": "Fraud record not found"}), 404

    data = request.get_json() or {}
    f.statut_analyse = "CONFIRME"
    f.analyste_id    = data.get("analyste_id", f.analyste_id)
    f.commentaire    = data.get("commentaire",  f.commentaire)

    tx = Transaction.query.get(f.transaction_id)
    if tx:
        tx.statut = "REJETEE"

    db.session.commit()
    return jsonify({"message": "Fraude confirmée, transaction rejetée"})


# ======================
# PUT /api/fraud/<id>/rejeter  → FAUX_POSITIF
# ======================
@fraud_bp.route("/api/fraud/<int:id>/rejeter", methods=["PUT"])
@jwt_required()
def rejeter_fraud(id):
    f = Fraud.query.get(id)
    if not f:
        return jsonify({"message": "Fraud record not found"}), 404

    data = request.get_json() or {}
    f.statut_analyse = "FAUX_POSITIF"
    f.analyste_id    = data.get("analyste_id", f.analyste_id)
    f.commentaire    = data.get("commentaire",  f.commentaire)

    tx = Transaction.query.get(f.transaction_id)
    if tx:
        tx.statut = "VALIDEE"

    db.session.commit()
    return jsonify({"message": "Faux positif enregistré, transaction validée"})


# ======================
# PUT /api/fraud/<id>/bloquer  → bloque le compte lié, statut RESOLU
# ======================
@fraud_bp.route("/api/fraud/<int:id>/bloquer", methods=["PUT"])
@jwt_required()
def bloquer_compte_fraud(id):
    f = Fraud.query.get(id)
    if not f:
        return jsonify({"message": "Fraud record not found"}), 404

    if f.statut_analyse != "CONFIRME":
        return jsonify({"message": "Seule une fraude confirmée peut entraîner un blocage"}), 400

    tx = Transaction.query.get(f.transaction_id)
    if not tx:
        return jsonify({"message": "Transaction associée introuvable"}), 404

    compte = Compte.query.get(tx.compte_id)
    if not compte:
        return jsonify({"message": "Compte associé introuvable"}), 404

    data = request.get_json() or {}
    compte.statut    = "BLOQUE"
    f.statut_analyse = "RESOLU"
    f.commentaire    = data.get("commentaire", f.commentaire)

    db.session.commit()
    return jsonify({"message": f"Compte #{compte.compte_id} bloqué, fraude résolue"})


# ======================
# PUT /api/fraud/<id>/reclassifier  → rouvre une fraude marquée FAUX_POSITIF
# ======================
@fraud_bp.route("/api/fraud/<int:id>/reclassifier", methods=["PUT"])
@jwt_required()
def reclassifier_fraud(id):
    f = Fraud.query.get(id)
    if not f:
        return jsonify({"message": "Fraud record not found"}), 404

    if f.statut_analyse != "FAUX_POSITIF":
        return jsonify({"message": "Seule une fraude 'faux positif' peut être reclassifiée"}), 400

    data = request.get_json() or {}
    f.statut_analyse = "EN_COURS"
    f.commentaire    = data.get("commentaire", f.commentaire)

    tx = Transaction.query.get(f.transaction_id)
    if tx:
        tx.statut = "EN_ANALYSE"

    db.session.commit()
    return jsonify({"message": "Fraude reclassifiée, remise en analyse"})


# ── helpers ──────────────────────────────────────────────
def _fmt_full(f):
    # score_ml en Oracle est entre 0-100 → normaliser en 0-1 pour le frontend
    score_raw = float(f.score_ml or 0)
    score_norm = score_raw / 100.0 if score_raw > 1 else score_raw

    return {
        "id":              f.fraud_id,
        "transaction_id":  f.transaction_id,
        "type_fraude":     f.type_fraude,
        "niveau_risque":   f.niveau_risque,
        "score_ml":        score_norm,
        "date_detection":  str(f.date_detection),
        "statut_analyse":  f.statut_analyse,
        "analyste_id":     f.analyste_id,
        "commentaire":     f.commentaire
    }