"""
Tests de l'authentification (/login) et de la protection JWT des routes.
Catégorie : intégration + sécurité.
"""
from tests.conftest import auth_header


def test_login_success_returns_token(client, seeded):
    resp = client.post("/login", json={
        "email": "julie.dupont@test.fr", "password": "MotDePasse123!"
    })
    assert resp.status_code == 200
    body = resp.get_json()
    assert "token" in body
    assert body["role"] == "banquier"
    assert body["client_id"] == seeded["client_id"]


def test_login_wrong_password_returns_401(client, seeded):
    resp = client.post("/login", json={
        "email": "julie.dupont@test.fr", "password": "mauvais-mdp"
    })
    assert resp.status_code == 401
    assert "token" not in resp.get_json()


def test_login_unknown_email_returns_401(client, seeded):
    resp = client.post("/login", json={
        "email": "inconnu@test.fr", "password": "peu-importe"
    })
    assert resp.status_code == 401


def test_login_missing_fields_returns_400(client):
    resp = client.post("/login", json={"email": "julie.dupont@test.fr"})
    assert resp.status_code == 400


def test_login_no_body_returns_400(client):
    resp = client.post("/login", content_type="application/json", data="")
    assert resp.status_code == 400


def test_login_suspended_account_returns_403(client, app, seeded):
    from app.extensions import db
    from app.models import Client
    with app.app_context():
        c = db.session.get(Client, seeded["client_id"])
        c.statut = "SUSPENDU"
        db.session.commit()

    resp = client.post("/login", json={
        "email": "julie.dupont@test.fr", "password": "MotDePasse123!"
    })
    assert resp.status_code == 403


def test_protected_route_without_token_returns_401(client):
    """Sécurité : une route protégée par @jwt_required() doit refuser l'accès sans token."""
    resp = client.get("/api/transactions")
    assert resp.status_code == 401


def test_protected_route_with_invalid_token_returns_422_or_401(client):
    resp = client.get("/api/transactions", headers={"Authorization": "Bearer token-invalide"})
    assert resp.status_code in (401, 422)


def test_protected_route_with_valid_token_succeeds(client, seeded):
    headers = auth_header(client)
    resp = client.get("/api/transactions", headers=headers)
    assert resp.status_code == 200


def test_password_never_returned_in_login_response(client, seeded):
    """RGPD/sécurité : le mot de passe (même hashé) ne doit jamais transiter dans la réponse."""
    resp = client.post("/login", json={
        "email": "julie.dupont@test.fr", "password": "MotDePasse123!"
    })
    body = resp.get_json()
    assert "mot_de_passe" not in body
    assert "password" not in body
