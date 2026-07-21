from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func, case
from app.models import Transaction, Fraud
from app.extensions import db

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/api/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    # Une seule requête agrégée au lieu de 6 (4 COUNT + 2 SUM séparés) :
    # SQLAlchemy génère un unique SELECT avec des agrégats conditionnels
    # (SUM(CASE WHEN ...)), donc un seul aller-retour vers Oracle au lieu de six.
    row = db.session.query(
        func.count(Transaction.transaction_id).label("total"),
        func.sum(case((Transaction.statut == "EN_ANALYSE", 1), else_=0)).label("fraud"),
        func.sum(case((Transaction.statut == "VALIDEE",    1), else_=0)).label("valid"),
        func.sum(case((Transaction.statut == "REJETEE",    1), else_=0)).label("rejected"),
        func.sum(case((Transaction.statut == "EN_ANALYSE", Transaction.montant), else_=0)).label("fraud_amount"),
        func.sum(Transaction.montant).label("total_amount"),
    ).one()

    total    = row.total or 0
    fraud    = row.fraud or 0
    valid    = row.valid or 0
    rejected = row.rejected or 0
    fraud_rate = round((fraud / total) * 100, 2) if total > 0 else 0

    pending = Fraud.query.filter_by(statut_analyse="EN_COURS").count()

    return jsonify({
        "total_transactions":    total,
        "fraud_count":           fraud,
        "safe_count":            valid,
        "rejected_transactions": rejected,
        "fraud_rate":            fraud_rate,
        "fraud_amount":          float(row.fraud_amount or 0),
        "total_amount":          float(row.total_amount or 0),
        "pending_alerts":        pending
    })