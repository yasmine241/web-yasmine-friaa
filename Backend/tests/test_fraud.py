
from tests.conftest import auth_header


def test_valider_fraud_confirms_and_rejects_transaction(client, seeded):
    headers = auth_header(client)
    resp = client.put(f"/api/fraud/{seeded['fraud_id']}/valider", headers=headers,
                       json={"analyste_id": "yasmine"})
    assert resp.status_code == 200

    tx = client.get(f"/api/transactions/{seeded['transaction_id']}", headers=headers).get_json()
    assert tx["statut"] == "REJETEE"


def test_rejeter_fraud_marks_false_positive_and_validates_transaction(client, seeded):
    headers = auth_header(client)
    resp = client.put(f"/api/fraud/{seeded['fraud_id']}/rejeter", headers=headers,
                       json={"analyste_id": "yasmine"})
    assert resp.status_code == 200

    tx = client.get(f"/api/transactions/{seeded['transaction_id']}", headers=headers).get_json()
    assert tx["statut"] == "VALIDEE"


def test_bloquer_compte_requires_confirmed_fraud_first(client, seeded):
    """Règle métier : on ne peut bloquer un compte que si la fraude a déjà été CONFIRME."""
    headers = auth_header(client)
    resp = client.put(f"/api/fraud/{seeded['fraud_id']}/bloquer", headers=headers, json={})
    assert resp.status_code == 400


def test_bloquer_compte_after_confirmation_succeeds(client, seeded):
    headers = auth_header(client)
    client.put(f"/api/fraud/{seeded['fraud_id']}/valider", headers=headers, json={})
    resp = client.put(f"/api/fraud/{seeded['fraud_id']}/bloquer", headers=headers, json={})
    assert resp.status_code == 200


def test_reclassifier_requires_faux_positif_first(client, seeded):
    headers = auth_header(client)
    resp = client.put(f"/api/fraud/{seeded['fraud_id']}/reclassifier", headers=headers, json={})
    assert resp.status_code == 400


def test_reclassifier_reopens_case(client, seeded):
    headers = auth_header(client)
    client.put(f"/api/fraud/{seeded['fraud_id']}/rejeter", headers=headers, json={})
    resp = client.put(f"/api/fraud/{seeded['fraud_id']}/reclassifier", headers=headers, json={})
    assert resp.status_code == 200

    updated = client.get(f"/api/fraud/{seeded['fraud_id']}", headers=headers).get_json()
    assert updated["statut_analyse"] == "EN_COURS"


def test_get_fraud_not_found_returns_404(client, seeded):
    headers = auth_header(client)
    resp = client.get("/api/fraud/999999", headers=headers)
    assert resp.status_code == 404


def test_pending_frauds_only_returns_en_cours(client, seeded):
    headers = auth_header(client)
    client.put(f"/api/fraud/{seeded['fraud_id']}/rejeter", headers=headers, json={})
    pending = client.get("/api/fraud/pending", headers=headers).get_json()
    assert all(f["statut_analyse"] == "EN_COURS" for f in pending)
