"""
Tests unitaires purs de la logique de scoring de fraude (app/services/fraud_detector.py).

Ces tests ciblent directement _rule_score(), le mode de repli utilisé
quand aucun modèle ML n'est chargé. Ils ne dépendent ni de Flask, ni de
la base de données : c'est le seul fichier de tests qui reste 100 %
déterministe même sans fraud_model.pkl.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.fraud_detector import FraudDetector, encode, PAYS_LIST, TYPE_LIST


def test_low_amount_same_country_is_not_flagged():
    score = FraudDetector._rule_score(montant=100, pays_o="France", pays_d="France")
    assert score < 0.7


def test_large_amount_cross_border_is_flagged():
    score = FraudDetector._rule_score(montant=15000, pays_o="France", pays_d="Russie")
    assert score >= 0.7


def test_score_is_always_clamped_between_0_and_1():
    score = FraudDetector._rule_score(montant=1_000_000, pays_o="France", pays_d="Chine")
    assert 0.0 <= score <= 1.0


def test_cross_border_alone_adds_partial_risk():
    same = FraudDetector._rule_score(montant=100, pays_o="France", pays_d="France")
    diff = FraudDetector._rule_score(montant=100, pays_o="France", pays_d="Chine")
    assert diff > same


def test_encode_unknown_value_defaults_to_zero():
    """Robustesse : un pays ou type inconnu (donnée corrompue) ne doit pas lever d'exception."""
    assert encode("Pays-Imaginaire", PAYS_LIST) == 0
    assert encode("TYPE_INCONNU", TYPE_LIST) == 0


def test_predict_without_model_uses_rule_fallback():
    """Si fraud_model.pkl est absent/illisible, predict() doit quand même renvoyer un résultat exploitable."""
    detector = FraudDetector()
    detector.model = None  # force explicitement le mode règles pour ce test
    result = detector.predict({
        "montant": 20000, "pays_origine": "France", "pays_destination": "Japon",
        "type_transaction": "VIREMENT",
    })
    assert set(result.keys()) == {"score", "fraud"}
    assert isinstance(result["fraud"], bool)
    assert 0.0 <= result["score"] <= 1.0
