
import re
from collections import defaultdict
from statistics import mean

LOG_PATH = "performance.log"

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
