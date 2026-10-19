# Project Notes

LLM-Prop takes a text description of a crystal as input and predicts its properties like band gap and volume as output.

## Day 2 - Dataset
TextEdge downloaded. Files: train.csv, validation.csv, test.csv in data/TextEdge_v.1/TextEdge_v.1/
Columns: material_id, formula, cif_structure, description, band_gap, volume, is_gap_direct
Input = description (text). Outputs = band_gap, volume, is_gap_direct.
