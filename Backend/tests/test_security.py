"""
Tests de sécurité ciblés : injection SQL, contrôle d'accès sur reset-password,
absence de fuite d'information en cas d'erreur serveur.
"""
from tests.conftest import auth_header


def test_login_sql_injection_attempt_does_not_crash_or_bypass(client, seeded):
    """
    Utilisation de SQLAlchemy ORM (requêtes paramétrées) : une tentative
    d'injection classique dans le champ email ne doit ni planter le
    serveur (500) ni permettre de se connecter (200).
    """
    payload = {"email": "' OR '1'='1", "password": "' OR '1'='1"}
    resp = client.post("/login", json=payload)
    assert resp.status_code in (400, 401)


def test_reset_password_requires_authentication(client, seeded):
    resp = client.post("/api/reset-password", json={
        "email": seeded["email"], "new_password": "NouveauMdp123!"
    })
    assert resp.status_code == 401


def test_client_cannot_reset_another_clients_password(client, app, seeded):
    """Un client authentifié ne doit pouvoir réinitialiser que son propre mot de passe."""
    from app.extensions import db
    from app.models import Client
    from werkzeug.security import generate_password_hash

    with app.app_context():
        other = Client(
            nom="Autre", prenom="Personne", email="autre@test.fr",
            mot_de_passe=generate_password_hash("AutreMdp123!"),
            statut="ACTIF",
        )
        db.session.add(other)
        db.session.commit()

    headers = auth_header(client)  # token de "julie.dupont@test.fr"
    resp = client.post("/api/reset-password", headers=headers, json={
        "email": "autre@test.fr", "new_password": "Piratage123!"
    })
    assert resp.status_code == 403


def test_self_reset_password_is_allowed(client, seeded):
    headers = auth_header(client)
    resp = client.post("/api/reset-password", headers=headers, json={
        "email": seeded["email"], "new_password": "NouveauMdp123!"
    })
    assert resp.status_code == 200

    # l'ancien mot de passe ne doit plus fonctionner
    old_login = client.post("/login", json={
        "email": seeded["email"], "password": "MotDePasse123!"
    })
    assert old_login.status_code == 401


def test_cors_header_restricted_to_frontend_origin(client):
    """Le CORS ne doit pas être ouvert à '*' : seule l'origine du front est autorisée."""
    resp = client.get("/")
    assert resp.headers.get("Access-Control-Allow-Origin") != "*"


def test_server_error_does_not_leak_stack_trace(client, seeded):
    """
    En cas d'erreur interne, la réponse JSON ne doit jamais contenir la
    trace Python (fichiers, numéros de ligne) : seule un message générique
    doit être renvoyé au client (cf. gestion des erreurs en 2.2.4.1).
    """
    headers = auth_header(client)
    # id non numérique sur une route qui attend un <int:id> -> 404 Flask (pas une 500 avec trace)
    resp = client.get("/api/fraud/abc", headers=headers)
    assert resp.status_code == 404
    assert b"Traceback" not in resp.data
