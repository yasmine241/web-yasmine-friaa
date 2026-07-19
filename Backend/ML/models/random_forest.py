"""
Entrainement du Random Forest pour la detection de fraude.
Dataset : ML/data/transactions.csv (5205 transactions, extrait de la base
fraud_db_1050clients.sql - 1050 clients, 1487 comptes, 5205 transactions, 619 alertes).

Features (4, alignees avec le cahier des charges) : MONTANT, TYPE_TRANSACTION,
PAYS_ORIGINE, PAYS_DESTINATION.
SCORE_RISQUE sert UNIQUEMENT a construire le label FRAUDE (>= 70) et n'est
volontairement PAS utilise comme feature, pour eviter toute fuite de donnees
(le score ne doit pas etre a la fois la cible et une entree du modele).

Lancer depuis le dossier Backend/ML/ :
    python models/random_forest.py
"""

import os
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder

# -- Chargement -----------------------------------------------------------
DATA_PATH  = os.path.join(os.path.dirname(__file__), "..", "data", "transactions.csv")
MODEL_OUT  = os.path.join(os.path.dirname(__file__), "..", "..", "app", "services", "fraud_model.pkl")
LABELS_OUT = os.path.join(os.path.dirname(__file__), "..", "..", "app", "services", "label_encoders.pkl")

df = pd.read_csv(DATA_PATH)
print(f"Colonnes disponibles : {list(df.columns)}")
print(f"Lignes : {len(df)}")

# Normalisation d'un doublon d'encodage releve dans les donnees sources
if "PAYS_DESTINATION" in df.columns:
    df["PAYS_DESTINATION"] = df["PAYS_DESTINATION"].replace({"Corée du Nord": "Coree du Nord"})

# -- Encodage ---------------------------------------------------------------
le_type   = LabelEncoder()
le_pays_o = LabelEncoder()
le_pays_d = LabelEncoder()

df["TYPE_TRANSACTION_ENC"] = le_type.fit_transform(df["TYPE_TRANSACTION"].astype(str))
df["PAYS_ORIGINE_ENC"]     = le_pays_o.fit_transform(df["PAYS_ORIGINE"].astype(str))
df["PAYS_DESTINATION_ENC"] = le_pays_d.fit_transform(df["PAYS_DESTINATION"].astype(str))

# Cible : fraude si score_risque >= 70 (SCORE_RISQUE n'entre PAS dans les features)
df["FRAUDE"] = (df["SCORE_RISQUE"] >= 70).astype(int)
print(f"Distribution fraude : {df['FRAUDE'].value_counts().to_dict()}")

X = df[["MONTANT", "TYPE_TRANSACTION_ENC", "PAYS_ORIGINE_ENC", "PAYS_DESTINATION_ENC"]]
y = df["FRAUDE"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# -- Entrainement -------------------------------------------------------
model = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

pred = model.predict(X_test)

print("\n=== Random Forest ===")
print("Accuracy :", accuracy_score(y_test, pred))
print(classification_report(y_test, pred))

# -- Sauvegarde -----------------------------------------------------------
os.makedirs(os.path.dirname(MODEL_OUT), exist_ok=True)
joblib.dump(model, MODEL_OUT)
joblib.dump({"type": le_type, "pays_o": le_pays_o, "pays_d": le_pays_d}, LABELS_OUT)

print(f"\nModele sauvegarde -> {MODEL_OUT}")
print(f"Encodeurs sauvegardes -> {LABELS_OUT}")
