"""Day 2: explore the TextEdge dataset (read only, changes nothing)."""
import sys
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Windows terminals can crash on symbols like the subscript in Na3Bi(P2O7)2
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "TextEdge_v.1" / "TextEdge_v.1"
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)

# cif_structure is huge and we do not need it, so we skip it
COLS = ["material_id", "description", "band_gap", "volume", "is_gap_direct"]

frames = {}
for name in ["train", "validation", "test"]:
    print(f"Reading {name}.csv ...")
    frames[name] = pd.read_csv(DATA / f"{name}.csv", usecols=COLS)

print("\n=== 1. HOW MANY ROWS ===")
for name, df in frames.items():
    print(f"{name:<11}: {len(df):>7} rows")

train = frames["train"]

print("\n=== 2. MISSING VALUES (train) ===")
print(train.isna().sum())

print("\n=== 3. BAND GAP (train) ===")
print(train["band_gap"].describe())
zero = (train["band_gap"] == 0).mean() * 100
print(f"Crystals with band gap = 0 (metals): {zero:.1f}%")

print("\n=== 4. VOLUME (train) ===")
print(train["volume"].describe())

print("\n=== 5. DIRECT vs INDIRECT (train) ===")
print(train["is_gap_direct"].value_counts())

print("\n=== 6. TEXT LENGTH IN WORDS (train) ===")
words = train["description"].fillna("").str.split().str.len()
print(words.describe())
print(f"Descriptions longer than 400 words: {(words > 400).mean() * 100:.1f}%")

print("\n=== 7. ONE SAMPLE DESCRIPTION ===")
row = train.iloc[0]
print("ID:", row["material_id"])
print(str(row["description"])[:700], "...")

# save two simple pictures for the report
fig, ax = plt.subplots(1, 2, figsize=(10, 3.5))
train["band_gap"].plot.hist(bins=50, ax=ax[0])
ax[0].set_title("Band gap (eV)")
words.plot.hist(bins=50, ax=ax[1])
ax[1].set_title("Description length (words)")
plt.tight_layout()
plt.savefig(RESULTS / "day2_distributions.png", dpi=120)
print("\nSaved picture:", RESULTS / "day2_distributions.png")
