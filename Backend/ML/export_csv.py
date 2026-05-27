import oracledb
import pandas as pd

# connexion Oracle
conn = oracledb.connect(
    user="system",
    password="2002",
    dsn="localhost:1521/XE"
)

# requête SQL (adapte table)
query = "SELECT * FROM TRANSACTIONS"

# lecture SQL -> dataframe
df = pd.read_sql(query, conn)

# export CSV
df.to_csv("transactions.csv", index=False)

print("CSV créé ✔")