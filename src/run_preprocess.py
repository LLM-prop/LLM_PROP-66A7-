"""Day 3: clean the FULL train / validation / test files and save them.

Usage (from the LLM_PROP folder, with (venv) on):
    python src/run_preprocess.py          -> Version A (authors' method)
    python src/run_preprocess.py B        -> Version B (element symbols protected)

Output: data/processed/<version>/train.csv, validation.csv, test.csv
Columns: material_id, description (cleaned), band_gap, volume, is_gap_direct (0/1)
"""
import sys
from pathlib import Path

import pandas as pd
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parent))
from preprocess import load_stopwords, preprocess_text  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "TextEdge_v.1" / "TextEdge_v.1"

version = sys.argv[1].upper() if len(sys.argv) > 1 else "A"
if version not in ("A", "B"):
    sys.exit("Version must be A or B")
keep_elements = version == "B"

OUT = ROOT / "data" / "processed" / version
OUT.mkdir(parents=True, exist_ok=True)

stop = load_stopwords()
print(f"Version {version}  |  stopwords: {len(stop)}  |  protect elements: {keep_elements}")

COLS = ["material_id", "description", "band_gap", "volume", "is_gap_direct"]
LABELS = ["band_gap", "volume", "is_gap_direct"]

for split in ["train", "validation", "test"]:
    print(f"\n--- {split} ---")
    df = pd.read_csv(DATA / f"{split}.csv", usecols=COLS)
    n0 = len(df)
    df = df.dropna(subset=LABELS + ["description"]).copy()
    print(f"rows: {n0}  ->  {len(df)} (dropped {n0 - len(df)} with missing values)")

    df["is_gap_direct"] = df["is_gap_direct"].map(
        {True: 1, False: 0, "True": 1, "False": 0}).astype(int)

    tqdm.pandas(desc=f"cleaning {split}")
    df["description"] = df["description"].progress_apply(
        lambda t: preprocess_text(t, stop, keep_elements))

    words = df["description"].str.split().str.len()
    print(f"words per text after cleaning: median {words.median():.0f}, mean {words.mean():.0f}, max {words.max()}")

    out_file = OUT / f"{split}.csv"
    df[COLS].to_csv(out_file, index=False)
    print("saved:", out_file)

print("\nDone. Version", version)
