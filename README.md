# SG SecureBank – Guide de démarrage

## 1. Base de données Oracle

```bash
# Importer le schéma SQL dans Oracle XE
sqlplus system/2002@localhost:1521/XE @fraud_db_1050clients_.sql
```

## 2. Backend (Flask + Oracle)

```bash
cd Backend
pip install -r requirements.txt

# Lancer le serveur
python run.py
# → API disponible sur http://127.0.0.1:5000
```

## 3. Entraîner le modèle ML (une seule fois)

```bash
cd Backend/ML
python models/random_forest.py
# → Génère app/services/fraud_model.pkl
```

## 4. Frontend

Servir le dossier `Frontend/` avec un serveur local :

```bash
cd Frontend
python -m http.server 8080
# → http://localhost:8080
```

## Identifiants de connexion

Utiliser un email/mot de passe d'un client **ACTIF** de la base Oracle.  
Les mots de passe dans le SQL sont hashés bcrypt.

Pour créer un compte de test rapidement :

```python
from werkzeug.security import generate_password_hash
print(generate_password_hash("motdepasse123"))
# Copier le hash dans la table clients
```

## Architecture

```
Backend/
├── app/
│   ├── routes/
│   │   ├── auth.py          ← login Oracle (corrigé)
│   │   ├── clients.py       ← CRUD /api/clients
│   │   ├── comptes.py       ← CRUD /api/comptes  (préfixes corrigés)
│   │   ├── transactions.py  ← CRUD /api/transactions
│   │   ├── fraud.py         ← alertes + /api/fraud/detect (ajouté)
│   │   └── dashboard.py     ← /api/dashboard
│   ├── services/
│   │   ├── fraud_detector.py ← charge fraud_model.pkl (corrigé)
│   │   └── fraud_model.pkl   ← généré par ML/models/random_forest.py
│   └── models.py
├── ML/
│   └── models/random_forest.py  ← entraînement + sauvegarde joblib
└── config.py  ← connexion Oracle

Frontend/
├── pages/
│   ├── login.html
│   ├── dashboard.html    ← 8 KPIs + graphique + alertes récentes
│   ├── clients.html      ← liste + ajout/suppression
│   ├── comptes.html      ← NOUVELLE PAGE
│   ├── transactions.html ← liste + formulaire création
│   └── fraud.html        ← liste alertes + validation + détection manuelle
└── assets/
    ├── css/style.css      ← rempli (était vide)
    ├── css/dashboard.css  ← rempli (était vide)
    └── js/
        ├── config.js      ← + toast, getUser
        ├── api.js         ← toutes les routes API
        └── *.js           ← mis à jour
```
