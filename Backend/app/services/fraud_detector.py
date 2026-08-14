import os
import joblib
import pandas as pd

MODEL_PATH = os.path.join(os.path.dirname(__file__), "fraud_model.pkl")

PAYS_LIST = [
    "Allemagne",
    "Belgique",
    "Brésil",
    "Chine",
    "Espagne",
    "Etats-Unis",
    "France",
    "Inde",
    "Italie",
    "Japon",
    "Maroc",
    "Pays-Bas",
    "Portugal",
    "Royaume-Uni",
    "Russie",
    "Sénégal",
    "Suisse",
    "Tunisie",
    "Turquie"
]

TYPE_LIST = [
    "DEPOT",
    "PAIEMENT_EN_LIGNE",
    "RETRAIT",
    "TRANSACTION_MOBILE",
    "VIREMENT"
]


def encode(value, lst):
    """
    Transforme une valeur textuelle en valeur numérique.
    Si la valeur n'existe pas dans la liste, retourne 0.
    """
    try:
        return lst.index(value)
    except (ValueError, AttributeError):
        return 0


class FraudDetector:

    def __init__(self):
        self.model = None
        self._load_model()

    def _load_model(self):
        """
        Charge le modèle Random Forest.
        """
        if os.path.exists(MODEL_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
                print("✅ Modèle ML chargé")
            except Exception as e:
                print(f"⚠️ Impossible de charger le modèle : {e}")
        else:
            print("⚠️ fraud_model.pkl introuvable — mode règles actif")

    def predict(self, transaction: dict) -> dict:
        """
        Analyse une transaction et retourne :
        - score : probabilité de fraude
        - fraud : True / False
        """

        # ==============================
        # Récupération des données
        # ==============================

        montant = float(transaction.get("montant", 0))

        pays_o = transaction.get(
            "pays_origine",
            "France"
        )

        pays_d = transaction.get(
            "pays_destination",
            "France"
        )

        type_tx = transaction.get(
            "type_transaction",
            "VIREMENT"
        )

        # ==============================
        # Prédiction avec le modèle ML
        # ==============================

        if self.model is not None:

            # Le modèle a été entraîné avec 4 features.
            # Il faut donc lui envoyer exactement 4 features.

            features = pd.DataFrame([{
                "montant": montant,
                "type_transaction": encode(type_tx, TYPE_LIST),
                "pays_origine": encode(pays_o, PAYS_LIST),
                "pays_destination": encode(pays_d, PAYS_LIST)
            }])

            try:
                proba = self.model.predict_proba(features)[0][1]

                return {
                    "score": round(float(proba), 2),
                    "fraud": bool(proba >= 0.7)
                }

            except Exception as e:
                print(f"⚠️ Erreur lors de la prédiction ML : {e}")

                # En cas d'erreur du modèle,
                # on utilise le système de règles.
                score = self._rule_score(
                    montant,
                    pays_o,
                    pays_d
                )

                return {
                    "score": round(score, 2),
                    "fraud": bool(score >= 0.7)
                }

        # ==============================
        # Mode règles si modèle absent
        # ==============================

        score = self._rule_score(
            montant,
            pays_o,
            pays_d
        )

        return {
            "score": round(score, 2),
            "fraud": bool(score >= 0.7)
        }

    @staticmethod
    def _rule_score(montant, pays_o, pays_d):
        """
        Calcule un score de risque basé sur des règles simples.
        """

        score = 0.0

        # Montant élevé
        if montant > 5000:
            score += 0.4

        # Montant très élevé
        if montant > 10000:
            score += 0.3

        # Transaction internationale
        if pays_o != pays_d:
            score += 0.3

        return min(score, 1.0)