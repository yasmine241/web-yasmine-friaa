# SG SecureBank — Application de détection de fraude bancaire

Projet de fin d'études — Yasmine FRIAA — NEXA Digital School (2025/2026)

## Liens

- URL publique : `http://localhost:8080 `
- Dépôt Git : `https://github.com/yasmine241/web-yasmine-friaa`

##  Description

SG SecureBank est une application web de détection de fraude dans les transactions
bancaires, combinant des modèles de Machine Learning (Random Forest) à une validation
humaine (approche Human-in-the-Loop). L'application permet aux analystes fraude de
consulter les transactions, gérer les alertes et superviser l'activité via un tableau
de bord interactif.

##  Prérequis d'installation

- Python 3.11+ (le projet a été testé en 3.11 et 3.14)
- Oracle Database XE (locale ou distante) — le driver oracledb est utilisé en mode thin, donc aucun Oracle Instant Client n'est nécessaire
- pip pour installer les dépendances Python
- Un navigateur récent (Chrome, Edge ou Firefox)
- Aucune dépendance Node.js : le frontend est en HTML/CSS/JS natif (Bootstrap via CDN)

##  Étapes d'installation

1. Base de données

Importer le dump SQL fourni (fraud_db_1050clients_.sql) dans une base Oracle XE, via SQL Developer ou sqlplus :

sql
sqlplus system/<votre_mot_de_passe>@localhost:1521/XE @fraud_db_1050clients_.sql

Ce script crée les 4 tables (CLIENTS, COMPTES, TRANSACTIONS, FRAUD) et insère 1050 clients de test avec leurs comptes et transactions.

Ensuite, appliquer la migration qui ajoute les clés étrangères et index manquants :

sql
sqlplus system/<votre_mot_de_passe>@localhost:1521/XE @Backend
migrations/001_contraintes_relationnelles.sql

2. Backend (Flask)

cd Backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   

pip install -r requirements.txt

Un fichier .env est déjà fourni à la racine du dossier Backend/ avec les identifiants Oracle et l'admin (voir Identifiants de test). Vérifier que ORACLE_DSN correspond à votre instance locale (localhost:1521/XE par défaut).

Lancer le serveur :


python run.py

L'API démarre sur http://localhost:5000. Vérification rapide : http://localhost:5000/ doit renvoyer {"message": "API SG SecureBank running"}.

3. Frontend

Le frontend est statique et pointe vers l'API via assets/js/config.js (API_URL = "http://localhost:5000", déjà configuré).


cd Frontend
python -m http.server 8080

Ouvrir http://localhost:8080/index.html (ou pages/login.html) dans le navigateur.

Le CORS backend n'autorise explicitement que http://localhost:8080 et http://127.0.0.1:8080 — servir le frontend sur un autre port nécessite d'ajouter l'origine dans Backend/app/__init__.py et .env (ALLOWED_ORIGINS).

4. Base de données

Type :	Oracle XE
DSN	: localhost:1521/XE
Utilisateur : system
Mot de passe :	2002
Client	: oracledb (mode thin, pas d'Instant Client requis)

5. Identifiants de test
Compte administrateur (back office)
	
Email	: yasmine@bank.com
Mot de passe	: yasmine123
Rôle :	administrateur (accès complet : gestion clients, comptes, transactions, fraude)

6. Compatibilité navigateurs

Testé sur :
-  Google Chrome
-  Mozilla Firefox
-  Microsoft Edge
-  Safari (validation partielle, non exhaustive)



7. Structure du projet
Backend/
├── app/
│   ├── routes/        # auth, clients, comptes, transactions, dashboard, fraud
│   ├── services/       # modèle ML (fraud_model.pkl) et logique métier
│   ├── models.py
│   └── extensions.py
├── ML/                  # scripts d'entraînement (Random Forest, export CSV)
├── migrations/          # 001_contraintes_relationnelles.sql
├── tests/               # pytest (auth, fraud, security, transactions)
├── config.py
├── run.py
└── requirements.txt

Frontend/
├── assets/{css,js}
├── components/          # navbar, sidebar, footer, cookie-banner
├── pages/                # login, dashboard, clients, comptes, transactions, fraud, cgu, mentions-légales
└── index.html

8. Lancer les tests


cd Backend
python -m pytest tests/ -v

Tests exécutés sur une base SQLite en mémoire (aucune connexion Oracle requise).

Stack : Flask + SQLAlchemy + Flask-JWT-Extended + Flask-CORS côté backend, Oracle XE comme SGBD, modèle Random Forest pour le scoring de fraude ; HTML/CSS/JS  + Bootstrap côté frontend.