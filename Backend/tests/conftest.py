"""
Configuration commune des tests SG SecureBank.

Les tests tournent sur une base SQLite en mémoire (jamais sur la base
Oracle réelle) : on crée l'app normalement via create_app(), puis on
substitue SQLALCHEMY_DATABASE_URI avant la première requête. Cela permet
de tester les routes Flask, les modèles et la logique métier sans
dépendre d'une instance Oracle XE disponible.
"""
import os
import sys
from datetime import date, datetime, timezone

import pytest
from werkzeug.security import generate_password_hash

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from app import create_app
from app.extensions import db
from app.models import Client, Compte, Transaction, Fraud

# La connexion Oracle est fixée dans Config au moment de l'import du module
# (SQLALCHEMY_DATABASE_URI construite dans le corps de la classe). On la
# remplace donc AVANT create_app(), car c'est create_app() qui appelle
# db.init_app(app) et crée l'engine SQLAlchemy à partir de cette valeur.
Config.SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


@pytest.fixture()
def app():
    application = create_app()
    application.config.update(TESTING=True)

    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def seeded(app):
    """Jeu de données minimal : 1 client actif, 1 compte, 1 transaction, 1 alerte fraude."""
    with app.app_context():
        c = Client(
            nom="Dupont", prenom="Julie", email="julie.dupont@test.fr",
            mot_de_passe=generate_password_hash("MotDePasse123!"),
            date_naissance=date(1990, 5, 12), pays="France", statut="ACTIF",
        )
        db.session.add(c)
        db.session.commit()

        compte = Compte(client_id=c.client_id, numero_compte="FR7630001007941234567890185",
                         type_compte="COURANT", solde=1500.0, statut="ACTIF")
        db.session.add(compte)
        db.session.commit()

        tx = Transaction(
            compte_id=compte.compte_id, type_transaction="VIREMENT", montant=250.0,
            pays_origine="France", pays_destination="France",
            date_transaction=datetime.now(timezone.utc), statut="VALIDEE", score_risque=0.12,
        )
        db.session.add(tx)
        db.session.commit()

        fraud = Fraud(
            transaction_id=tx.transaction_id, type_fraude="TRANSACTION_INHABITUELLE",
            niveau_risque="ELEVE", score_ml=82.0, statut_analyse="EN_COURS",
        )
        db.session.add(fraud)
        db.session.commit()

        return {
            "client_id": c.client_id, "email": c.email,
            "compte_id": compte.compte_id,
            "transaction_id": tx.transaction_id,
            "fraud_id": fraud.fraud_id,
        }


def auth_header(client, email="julie.dupont@test.fr", password="MotDePasse123!"):
    resp = client.post("/login", json={"email": email, "password": password})
    token = resp.get_json()["token"]
    return {"Authorization": f"Bearer {token}"}
