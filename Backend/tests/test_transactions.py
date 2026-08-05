"""
Tests des transactions : création, consultation, pagination.
Catégorie : intégration.
"""
from tests.conftest import auth_header


def test_create_transaction_success(client, seeded):
    headers = auth_header(client)
    resp = client.post("/api/transactions", headers=headers, json={
        "compte_id": seeded["compte_id"],
        "montant": 120.0,
        "type_transaction": "VIREMENT",
        "pays_origine": "France",
        "pays_destination": "France",
    })
    assert resp.status_code == 201
    body = resp.get_json()
    assert 0.0 <= body["score_risque"] <= 1.0
    assert body["statut"] in ("VALIDEE", "EN_ANALYSE")


def test_create_transaction_missing_field_returns_400(client, seeded):
    headers = auth_header(client)
    resp = client.post("/api/transactions", headers=headers, json={
        "compte_id": seeded["compte_id"], "montant": 120.0
        # type_transaction manquant
    })
    assert resp.status_code == 400


def test_create_transaction_negative_amount_rejected(client, seeded):
    headers = auth_header(client)
    resp = client.post("/api/transactions", headers=headers, json={
        "compte_id": seeded["compte_id"], "montant": -50.0,
        "type_transaction": "VIREMENT",
    })
    assert resp.status_code == 400


def test_create_transaction_non_numeric_amount_rejected(client, seeded):
    headers = auth_header(client)
    resp = client.post("/api/transactions", headers=headers, json={
        "compte_id": seeded["compte_id"], "montant": "abc",
        "type_transaction": "VIREMENT",
    })
    assert resp.status_code == 400


def test_high_risk_transaction_creates_fraud_alert(client, seeded):
    """Une transaction à fort montant, pays différents, doit déclencher une alerte (mode règles)."""
    headers = auth_header(client)
    resp = client.post("/api/transactions", headers=headers, json={
        "compte_id": seeded["compte_id"], "montant": 50000.0,
        "type_transaction": "VIREMENT",
        "pays_origine": "France", "pays_destination": "Russie",
    })
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["fraud"] is True
    assert body["statut"] == "EN_ANALYSE"


def test_get_transaction_not_found_returns_404(client, seeded):
    headers = auth_header(client)
    resp = client.get("/api/transactions/999999", headers=headers)
    assert resp.status_code == 404


def test_transactions_list_is_paginated(client, seeded):
    headers = auth_header(client)
    resp = client.get("/api/transactions?page=1&per_page=1", headers=headers)
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["per_page"] == 1
    assert len(body["items"]) <= 1


def test_transactions_per_page_is_capped_at_200(client, seeded):
    """Sécurité anti-abus : per_page ne doit jamais dépasser 200 même si demandé plus."""
    headers = auth_header(client)
    resp = client.get("/api/transactions?per_page=5000", headers=headers)
    assert resp.status_code == 200
    assert resp.get_json()["per_page"] == 200
