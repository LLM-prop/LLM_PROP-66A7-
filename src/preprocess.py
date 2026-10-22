"""Day 3 - Block 2 (Text Preparation), part 1: clean the description text.

Follows the recipe of the LLM-Prop authors:
  1. replace bond distances  (like 2.30-2.41 Angstrom)  with [NUM]
  2. replace bond angles     (like 120.5 degrees)       with [ANG]
  3. remove stopwords        (the, is, of, ...)
[CLS] is added later, in the tokenizing step.

Two versions (for the ablation study):
  Version A = the authors' method (keep_elements=False)
  Version B = same, but element symbols like O, Mg, Si are protected (keep_elements=True)

Run this file to test the cleaning on real crystal texts.
"""
import re
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

# Windows terminals can crash on symbols like subscripts, so be safe
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
STOPWORD_DIR = ROOT / "data" / "LLM-Prop-ref" / "stopwords" / "en"
VALID_CSV = ROOT / "data" / "TextEdge_v.1" / "TextEdge_v.1" / "validation.csv"

# The authors keep the words one..nine in the text (they carry the number of
# neighbours, like 'bonded to five O atoms'), so these are NOT stopwords.
NUMBER_WORDS = {"one", "two", "three", "four", "five", "six", "seven", "eight", "nine"}

# All 118 chemical element symbols. Used by Version B so they are never deleted.
ELEMENTS = set((
    "H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn "
    "Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce "
    "Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn "
    "Fr Ra Ac Th Pa U Np Pu Am Cm Bk Cf Es Fm Md No Lr Rf Db Sg Bh Hs Mt Ds Rg Cn Nh "
    "Fl Mc Lv Ts Og"
).split())
# These symbols are also normal English words ('In the first site'), so we cannot
# protect them without keeping lots of real stopwords.
AMBIGUOUS = {"I", "In", "As", "At", "Be", "No", "He", "Am"}
PROTECTED = ELEMENTS - AMBIGUOUS

# a number like 2.30 or a range like 2.30-2.41 (en-dash or normal dash), then a unit
_NUMBER = r"\d+(?:\.\d+)?(?:[–-]\d+(?:\.\d+)?)?\s*"
BOND_LENGTH = re.compile(_NUMBER + "[ÅÅ]")   # Angstrom sign (two possible characters)
ANGLE_SIGN = re.compile(_NUMBER + "°")             # degree sign
ANGLE_WORD = re.compile(_NUMBER + "degrees")            # the word 'degrees'


def load_stopwords(folder=STOPWORD_DIR):
    """Merge every .txt list in the folder into one set of lowercase words."""
    files = sorted(Path(folder).glob("*.txt"))
    if not files:
        raise FileNotFoundError(f"No stopword .txt files found in {folder}")
    words = set()
    for f in files:
        for line in f.read_text(encoding="utf-8", errors="ignore").splitlines():
            w = line.strip().lower()
            if w and not w.isdigit():          # drop empty lines and pure numbers
                words.add(w)
    return words - NUMBER_WORDS                 # keep one..nine in the text


def replace_num_and_ang(text):
    text = BOND_LENGTH.sub("[NUM]", text)
    text = ANGLE_SIGN.sub("[ANG]", text)
    text = ANGLE_WORD.sub("[ANG]", text)
    return text


def remove_stopwords(text, stopwords, keep_elements=False):
    kept = []
    for w in text.split():
        if keep_elements and w in PROTECTED:     # Version B: never delete an element symbol
            kept.append(w)
        elif w.lower() not in stopwords:
            kept.append(w)
    return " ".join(kept)


def preprocess_text(text, stopwords, keep_elements=False):
    """Replace distances/angles FIRST (so they are protected), then drop stopwords."""
    return remove_stopwords(replace_num_and_ang(str(text)), stopwords, keep_elements)


if __name__ == "__main__":
    stop = load_stopwords()
    print(f"Stopwords loaded: {len(stop)} unique words from {len(list(STOPWORD_DIR.glob('*.txt')))} files")

    df = pd.read_csv(VALID_CSV, usecols=["description"], nrows=2000)
    texts = df["description"].fillna("").tolist()

    print("\n=== BEFORE (first 500 characters of crystal 1) ===")
    print(texts[0][:500])
    cleaned0 = preprocess_text(texts[0], stop)
    print("\n=== AFTER ===")
    print(cleaned0[:500])

    before = sum(len(t.split()) for t in texts)
    cleaned = [preprocess_text(t, stop) for t in texts]
    after = sum(len(t.split()) for t in cleaned)
    print(f"\nOn {len(texts)} crystals: {before} words  ->  {after} words "
          f"({100 * (before - after) / before:.1f} percent removed)")
    print("[NUM] count:", sum(t.count("[NUM]") for t in cleaned))
    print("[ANG] count:", sum(t.count("[ANG]") for t in cleaned))
    print("Any Angstrom or degree sign left:",
          sum(("Å" in t) or ("Å" in t) or ("°" in t) for t in cleaned), "texts")

    cleaned_b = [preprocess_text(t, stop, keep_elements=True) for t in texts]
    after_b = sum(len(t.split()) for t in cleaned_b)
    print(f"Version B (protect elements) keeps {after_b - after} more words than Version A "
          f"({after_b} vs {after})")

    removed = Counter()
    for t in texts:
        for w in replace_num_and_ang(t).split():
            if w.lower() in stop:
                removed[w] += 1
    print("\nTop 15 removed words:", removed.most_common(15))
    short = [(w, n) for w, n in removed.most_common() if len(w) <= 2 and w.isalpha()]
    print("Removed 1-2 letter words (could some be chemical elements?):", short[:12])
