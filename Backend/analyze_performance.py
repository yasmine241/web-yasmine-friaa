"""
Analyse le fichier performance.log généré automatiquement par le middleware
Flask (voir app/__init__.py, before_request/after_request) et produit un
résumé par endpoint : nombre d'appels, temps de réponse moyen/min/max.

Utilisation :
    1. Lance l'application et utilise-la normalement pendant quelques minutes
       (navigue dans le dashboard, les transactions, les fraudes...) pour
       accumuler des lignes dans performance.log.
    2. Lance ce script depuis le dossier Backend/ :
           python analyze_performance.py
    3. Copie le tableau affiché dans le rapport (section "Mesures de
       performance"), avec les vrais chiffres mesurés sur ta machine.
"""
import re
from collections import defaultdict
from statistics import mean

LOG_PATH = "performance.log"
# Exemple de ligne : "2026-07-20 10:12:03,123 | GET /api/dashboard -> 200 in 42.3 ms"
PATTERN = re.compile(r"\| (\w+) (\S+) -> (\d+) in ([\d.]+) ms")

def main():
    stats = defaultdict(list)
    try:
        with open(LOG_PATH, encoding="utf-8") as f:
            for line in f:
                m = PATTERN.search(line)
                if m:
                    method, path, status, ms = m.groups()
                    key = f"{method} {path}"
                    stats[key].append(float(ms))
    except FileNotFoundError:
        print(f"Fichier {LOG_PATH} introuvable. Utilise l'application d'abord "
              f"pour générer des mesures.")
        return

    if not stats:
        print("Aucune mesure trouvée dans le log.")
        return

    print(f"{'Endpoint':<40} {'Appels':>7} {'Moy (ms)':>10} {'Min (ms)':>10} {'Max (ms)':>10}")
    print("-" * 80)
    for key, values in sorted(stats.items(), key=lambda kv: -mean(kv[1])):
        print(f"{key:<40} {len(values):>7} {mean(values):>10.1f} {min(values):>10.1f} {max(values):>10.1f}")

if __name__ == "__main__":
    main()
