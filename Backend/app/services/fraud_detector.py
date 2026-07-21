import os, joblib, numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), "fraud_model.pkl")

PAYS_LIST = ["Allemagne","Belgique","Brésil","Chine","Espagne","Etats-Unis",
             "France","Inde","Italie","Japon","Maroc","Pays-Bas","Portugal",
             "Royaume-Uni","Russie","Sénégal","Suisse","Tunisie","Turquie"]
TYPE_LIST = ["DEPOT","PAIEMENT_EN_LIGNE","RETRAIT","TRANSACTION_MOBILE","VIREMENT"]

def encode(value, lst):
    try:    return lst.index(value)
    except: return 0

class FraudDetector:
    def __init__(self):
        self.model = None
        self._load_model()

    def _load_model(self):
        if os.path.exists(MODEL_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
                print(f"✅ Modèle ML chargé")
            except Exception as e:
                print(f"⚠️ Impossible de charger le modèle : {e}")
        else:
            print("⚠️ fraud_model.pkl introuvable — mode règles actif")

    def predict(self, transaction: dict) -> dict:
        montant  = float(transaction.get("montant", 0))
        pays_o   = transaction.get("pays_origine",     "France")
        pays_d   = transaction.get("pays_destination", "France")
        type_tx  = transaction.get("type_transaction", "VIREMENT")

        if self.model is not None:
            features = np.array([[
                montant,
                encode(type_tx, TYPE_LIST),
                encode(pays_o,  PAYS_LIST),
                encode(pays_d,  PAYS_LIST)
            ]])
            proba = self.model.predict_proba(features)[0][1]
            return {"score": round(float(proba), 2), "fraud": bool(proba >= 0.7)}

        score = self._rule_score(montant, pays_o, pays_d)
        return {"score": round(score, 2), "fraud": score >= 0.7}

    @staticmethod
    def _rule_score(montant, pays_o, pays_d):
        score = 0.0
        if montant > 5000:  score += 0.4
        if montant > 10000: score += 0.3
        if pays_o != pays_d: score += 0.3
        return min(score, 1.0)