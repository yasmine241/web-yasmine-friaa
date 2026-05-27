import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder

# Chargement des données
df = pd.read_csv("data/transactions.csv")

# Encodage des colonnes catégorielles
le_type = LabelEncoder()
le_pays_o = LabelEncoder()
le_pays_d = LabelEncoder()

df["TYPE_TRANSACTION_ENC"] = le_type.fit_transform(df["TYPE_TRANSACTION"])
df["PAYS_ORIGINE_ENC"]     = le_pays_o.fit_transform(df["PAYS_ORIGINE"])
df["PAYS_DESTINATION_ENC"] = le_pays_d.fit_transform(df["PAYS_DESTINATION"])

# Création de la cible : fraude = score_risque >= 70
df["FRAUDE"] = (df["SCORE_RISQUE"] >= 70).astype(int)

# Features disponibles dans le CSV
X = df[["MONTANT", "TYPE_TRANSACTION_ENC", "PAYS_ORIGINE_ENC", "PAYS_DESTINATION_ENC", "SCORE_RISQUE"]]
y = df["FRAUDE"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = DecisionTreeClassifier(random_state=42)
model.fit(X_train, y_train)

pred = model.predict(X_test)

print("=== Decision Tree ===")
print("Accuracy:", accuracy_score(y_test, pred))
print(classification_report(y_test, pred))
