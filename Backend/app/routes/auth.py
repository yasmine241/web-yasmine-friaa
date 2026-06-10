import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash, generate_password_hash
from app.extensions import db, limiter
from app.models import Client

auth_bp = Blueprint("auth", __name__)

# ── Identifiants admin lus depuis l'environnement ────────────────────────────
# En production : définissez ADMIN_EMAIL et ADMIN_PASSWORD_HASH dans .env
# Pour générer le hash : from werkzeug.security import generate_password_hash
#                        print(generate_password_hash("votre_mot_de_passe"))
_ADMIN_EMAIL         = os.environ.get("ADMIN_EMAIL",         "yasmine@bank.com")
_ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH", "")

# Hash de secours pour le développement uniquement (mot de passe : yasmine123)
# Retirez cette ligne et définissez ADMIN_PASSWORD_HASH dans .env pour la production
_DEV_FALLBACK_PASSWORD = "yasmine123"


def _check_admin_password(password: str) -> bool:
    """Vérifie le mot de passe admin. Supporte hash bcrypt ou mot de passe dev."""
    if _ADMIN_PASSWORD_HASH and _ADMIN_PASSWORD_HASH.startswith("$2b$"):
        return check_password_hash(_ADMIN_PASSWORD_HASH, password)
    # Mode développement : comparaison directe (à remplacer en production)
    return password == _DEV_FALLBACK_PASSWORD


def _error(message: str, status: int):
    """Réponse d'erreur normalisée."""
    return jsonify({"success": False, "message": message}), status


# ── POST /login ──────────────────────────────────────────────────────────────
@auth_bp.route("/login", methods=["POST"])
@limiter.limit("10 per minute")          # Anti brute-force : 10 tentatives/min par IP
def login():
    data = request.get_json(silent=True)
    if not data:
        return _error("Données JSON manquantes.", 400)

    email    = (data.get("email")    or "").strip().lower()
    password = (data.get("password") or "").strip()

    if not email or not password:
        return _error("Email et mot de passe requis.", 400)

    # ── Vérification admin ───────────────────────────────────────────────────
    if email == _ADMIN_EMAIL.lower() and _check_admin_password(password):
        token = create_access_token(identity="admin")
        return jsonify({
            "success":   True,
            "message":   "Connexion réussie.",
            "token":     token,
            "role":      "admin",
            "client_id": 0,
            "nom":       "Admin",
            "prenom":    "SG SecureBank"
        }), 200

    # ── Vérification client ──────────────────────────────────────────────────
    try:
        client = Client.query.filter_by(email=email).first()
        if not client:
            # Message identique quelle que soit la raison (évite l'énumération)
            return _error("Identifiants incorrects.", 401)

        raw = client.mot_de_passe or ""
        if raw.startswith("$2b$") and len(raw) == 60:
            pwd_ok = check_password_hash(raw, password)
        else:
            # Mot de passe non hashé en base (legacy)
            pwd_ok = (password == raw)

        if not pwd_ok:
            return _error("Identifiants incorrects.", 401)

        if client.statut != "ACTIF":
            return _error("Compte suspendu ou clôturé. Contactez votre conseiller.", 403)

        token = create_access_token(identity=str(client.client_id))
        return jsonify({
            "success":   True,
            "message":   "Connexion réussie.",
            "token":     token,
            "role":      "banquier",
            "client_id": client.client_id,
            "nom":       client.nom,
            "prenom":    client.prenom
        }), 200

    except Exception as e:
        # On log l'erreur mais on ne l'expose pas au client
        print(f"[AUTH ERROR] {e}")
        return _error("Erreur serveur. Réessayez dans quelques instants.", 500)


# ── POST /api/reset-password ─────────────────────────────────────────────────
@auth_bp.route("/api/reset-password", methods=["POST"])
@limiter.limit("5 per minute")
def reset_password():
    data   = request.get_json(silent=True) or {}
    email  = (data.get("email")        or "").strip().lower()
    newpwd = (data.get("new_password") or "").strip()

    if not email or not newpwd:
        return _error("Email et nouveau mot de passe requis.", 400)

    if len(newpwd) < 8:
        return _error("Le mot de passe doit contenir au moins 8 caractères.", 400)

    client = Client.query.filter_by(email=email).first()
    if not client:
        # Message identique pour éviter l'énumération d'emails
        return jsonify({"success": True, "message": "Si cet email existe, un lien a été envoyé."}), 200

    client.mot_de_passe = generate_password_hash(newpwd)
    db.session.commit()
    return jsonify({"success": True, "message": "Mot de passe mis à jour avec succès."})
