from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.models import Transaction, Fraud
from app.extensions import db

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/api/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    total    = Transaction.query.count()
    fraud    = Transaction.query.filter_by(statut="EN_ANALYSE").count()
    valid    = Transaction.query.filter_by(statut="VALIDEE").count()
    rejected = Transaction.query.filter_by(statut="REJETEE").count()
    fraud_rate   = round((fraud / total) * 100, 2) if total > 0 else 0
    fraud_amount = db.session.query(db.func.sum(Transaction.montant)).filter_by(statut="EN_ANALYSE").scalar() or 0
    total_amount = db.session.query(db.func.sum(Transaction.montant)).scalar() or 0
    pending      = Fraud.query.filter_by(statut_analyse="EN_COURS").count()
    return jsonify({
        "total_transactions":    total,
        "fraud_count":           fraud,
        "safe_count":            valid,
        "rejected_transactions": rejected,
        "fraud_rate":            fraud_rate,
        "fraud_amount":          float(fraud_amount),
        "total_amount":          float(total_amount),
        "pending_alerts":        pending
    })