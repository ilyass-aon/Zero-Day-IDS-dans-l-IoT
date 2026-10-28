import pandas as pd
from pathlib import Path

# Racine du projet 
ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
REPORTS = ROOT / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)   # crée reports/ si absent

rows, type_counts = [], []

csv_files = sorted(RAW.rglob("*.csv"))
print(f"{len(csv_files)} fichiers CSV trouvés dans {RAW}")

for f in csv_files:
    try:
        df = pd.read_csv(f, low_memory=False)
    except Exception as e:
        print(f"Erreur {f}: {e}")
        continue

    source = f.parent.name
    time_cols = [c for c in df.columns if c.lower() in ("ts", "date", "time", "timestamp")]
    id_cols = [c for c in df.columns if c.lower() in
               ("src_ip", "dst_ip", "src_port", "dst_port", "device", "pid")]

    rows.append({
        "source": source,
        "fichier": f.name,
        "lignes": len(df),
        "colonnes": df.shape[1],
        "manquants_%": round(df.isna().mean().mean() * 100, 2),
        "doublons": int(df.duplicated().sum()),
        "col_temps": ",".join(time_cols),
        "col_id": ",".join(id_cols),
        "a_label": "label" in df.columns,
        "a_type": "type" in df.columns,
    })

    if "type" in df.columns:
        for t, n in df["type"].value_counts().items():
            type_counts.append({"source": source, "fichier": f.name, "type": t, "n": n})

if not rows:
    raise SystemExit("Aucun CSV lisible : vérifie que les données sont dans data/raw/")

inventaire = pd.DataFrame(rows)
attaques = pd.DataFrame(type_counts)

inventaire.to_csv(REPORTS / "inventaire_fichiers.csv", index=False)

if not attaques.empty:
    matrice = attaques.pivot_table(index="type", columns="source",
                                   values="n", aggfunc="sum", fill_value=0)
    matrice.to_csv(REPORTS / "matrice_source_attaque.csv")
    print(matrice)

print(inventaire.to_string())