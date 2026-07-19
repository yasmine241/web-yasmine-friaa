import os, joblib, numpy as np

MODEL_PATH    = os.path.join(os.path.dirname(__file__), "fraud_model.pkl")
ENCODERS_PATH = os.path.join(os.path.dirname(__file__), "label_encoders.pkl")


def encode(value, encoder):
    """Encode une valeur categorielle avec le LabelEncoder entraine.
    Retourne 0 si la valeur n'a jamais ete vue a l'entrainement
    (evite un crash sur une categorie inconnue en production)."""
    try:
        return int(encoder.transform([value])[0])
    except ValueError:
        return 0


class FraudDetector:
    def __init__(self):
        self.model = None
        self.encoders = None
        self._load_model()

    def _load_model(self):
        if os.path.exists(MODEL_PATH) and os.path.exists(ENCODERS_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
                self.encoders = joblib.load(ENCODERS_PATH)
                print("Modele ML et encodeurs charges")
            except Exception as e:
                print(f"Impossible de charger le modele : {e}")
        else:
            print("fraud_model.pkl ou label_encoders.pkl introuvable - mode regles actif")

    def predict(self, transaction: dict) -> dict:
        montant  = float(transaction.get("montant", 0))
        pays_o   = transaction.get("pays_origine",     "France")
        pays_d   = transaction.get("pays_destination", "France")
        type_tx  = transaction.get("type_transaction", "VIREMENT")

        if self.model is not None and self.encoders is not None:
            features = np.array([[
                montant,
                encode(type_tx, self.encoders["type"]),
                encode(pays_o,  self.encoders["pays_o"]),
                encode(pays_d,  self.encoders["pays_d"]),
            ]])
            proba = self.model.predict_proba(features)[0][1]
            return {"score": round(float(proba), 2), "fraud": bool(proba >= 0.7)}

        score = self._rule_score(montant, pays_o, pays_d)
        return {"score": round(score, 2), "fraud": score >= 0.7}

    @staticmethod
    def _rule_score(montant, pays_o, pays_d):
        """Repli utilise uniquement si le modele ML n'a pas pu etre charge."""
        score = 0.0
        if montant > 5000:  score += 0.4
        if montant > 10000: score += 0.3
        if pays_o != pays_d: score += 0.3
        return min(score, 1.0)
