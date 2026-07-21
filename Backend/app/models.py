from app.extensions import db
from datetime import datetime

# ============================================================
# CLIENTS
# ============================================================
class Client(db.Model):
    __tablename__ = "clients"

    client_id      = db.Column(db.Integer, primary_key=True)
    nom            = db.Column(db.String(100), nullable=False)
    prenom         = db.Column(db.String(100), nullable=False)
    email          = db.Column(db.String(150), nullable=False, unique=True, index=True)
    mot_de_passe   = db.Column(db.String(255), nullable=False)
    telephone      = db.Column(db.String(20))
    date_naissance = db.Column(db.Date)
    adresse        = db.Column(db.String(255))
    pays           = db.Column(db.String(100))
    date_creation  = db.Column(db.DateTime, default=datetime.utcnow)
    statut         = db.Column(db.String(20), default="ACTIF", index=True)

    comptes = db.relationship("Compte", backref="client", lazy="select")


# ============================================================
# COMPTES
# ============================================================
class Compte(db.Model):
    __tablename__ = "comptes"

    compte_id      = db.Column(db.Integer, primary_key=True)
    client_id      = db.Column(db.Integer, db.ForeignKey("clients.client_id"), nullable=False, index=True)
    numero_compte  = db.Column(db.String(34), nullable=False, unique=True)
    type_compte    = db.Column(db.String(20), default="COURANT")
    solde          = db.Column(db.Float, default=0.0)
    devise         = db.Column(db.String(10), default="EUR")
    date_ouverture = db.Column(db.Date, default=datetime.utcnow)
    statut         = db.Column(db.String(20), default="ACTIF", index=True)

    transactions = db.relationship("Transaction", backref="compte", lazy="select")


# ============================================================
# TRANSACTIONS
# ============================================================
class Transaction(db.Model):
    __tablename__ = "transactions"

    transaction_id     = db.Column(db.Integer, primary_key=True)
    compte_id          = db.Column(db.Integer, db.ForeignKey("comptes.compte_id"), nullable=False, index=True)
    type_transaction    = db.Column(db.String(30), nullable=False)
    montant             = db.Column(db.Float, nullable=False)
    devise              = db.Column(db.String(10), default="EUR")
    pays_origine        = db.Column(db.String(100), nullable=False)
    pays_destination    = db.Column(db.String(100), nullable=False)
    date_transaction    = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    ip_adresse          = db.Column(db.String(50))
    statut              = db.Column(db.String(20), default="EN_ANALYSE", index=True)
    score_risque        = db.Column(db.Float)

    frauds = db.relationship("Fraud", backref="transaction", lazy="select")


# ============================================================
# FRAUD
# ============================================================
class Fraud(db.Model):
    __tablename__ = "fraud"

    fraud_id        = db.Column(db.Integer, primary_key=True)
    transaction_id  = db.Column(db.Integer, db.ForeignKey("transactions.transaction_id"), nullable=False, index=True)
    type_fraude     = db.Column(db.String(50))
    niveau_risque   = db.Column(db.String(20))
    score_ml        = db.Column(db.Float)
    date_detection  = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    statut_analyse  = db.Column(db.String(20), default="EN_COURS", index=True)
    analyste_id     = db.Column(db.String(50))
    commentaire     = db.Column(db.String(500))
