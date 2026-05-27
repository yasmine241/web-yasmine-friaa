import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder, StandardScaler

# Chargement des données
df = pd.read_csv("data/transactions.csv")

# Encodage
le_type  = LabelEncoder()
le_pays_o = LabelEncoder()
le_pays_d = LabelEncoder()

df["TYPE_TRANSACTION_ENC"] = le_type.fit_transform(df["TYPE_TRANSACTION"])
df["PAYS_ORIGINE_ENC"]     = le_pays_o.fit_transform(df["PAYS_ORIGINE"])
df["PAYS_DESTINATION_ENC"] = le_pays_d.fit_transform(df["PAYS_DESTINATION"])

df["FRAUDE"] = (df["SCORE_RISQUE"] >= 70).astype(int)

X = df[["MONTANT", "TYPE_TRANSACTION_ENC", "PAYS_ORIGINE_ENC", "PAYS_DESTINATION_ENC", "SCORE_RISQUE"]]
y = df["FRAUDE"]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

model = LogisticRegression(max_iter=1000, random_state=42)
model.fit(X_train, y_train)

pred = model.predict(X_test)

print("=== Logistic Regression ===")
print("Accuracy:", accuracy_score(y_test, pred))
print(classification_report(y_test, pred))
