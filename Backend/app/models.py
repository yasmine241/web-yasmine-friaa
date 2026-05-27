from app.extensions import db
# CLIENTS
class Client(db.Model):
    __tablename__ = "clients"

    client_id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100))
    prenom = db.Column(db.String(100))
    email = db.Column(db.String(150))
    mot_de_passe = db.Column(db.String(255))
    telephone = db.Column(db.String(20))
    date_naissance = db.Column(db.Date)
    adresse = db.Column(db.String(255))
    pays = db.Column(db.String(100))
    date_creation = db.Column(db.DateTime)
    statut = db.Column(db.String(20))


# COMPTES
class Compte(db.Model):
    __tablename__ = "comptes"

    compte_id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer)
    numero_compte = db.Column(db.String(34))
    type_compte = db.Column(db.String(20))
    solde = db.Column(db.Float)
    devise = db.Column(db.String(10))
    date_ouverture = db.Column(db.Date)
    statut = db.Column(db.String(20))


# TRANSACTIONS
class Transaction(db.Model):
    __tablename__ = "transactions"

    transaction_id = db.Column(db.Integer, primary_key=True)
    compte_id = db.Column(db.Integer)
    type_transaction = db.Column(db.String(30))
    montant = db.Column(db.Float)
    devise = db.Column(db.String(10))
    pays_origine = db.Column(db.String(100))
    pays_destination = db.Column(db.String(100))
    date_transaction = db.Column(db.DateTime)
    ip_adresse = db.Column(db.String(50))
    statut = db.Column(db.String(20))
    score_risque = db.Column(db.Float)

# FRAUD

class Fraud(db.Model):
    __tablename__ = "fraud"

    fraud_id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer)
    type_fraude = db.Column(db.String(50))
    niveau_risque = db.Column(db.String(20))
    score_ml = db.Column(db.Float)
    date_detection = db.Column(db.DateTime)
    statut_analyse = db.Column(db.String(20))
    analyste_id = db.Column(db.String(50))
    commentaire = db.Column(db.String(500))