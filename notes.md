# Project Notes

LLM-Prop takes a text description of a crystal as input and predicts its properties like band gap and volume as output.

## Day 2 - Dataset
TextEdge downloaded. Files: train.csv, validation.csv, test.csv in data/TextEdge_v.1/TextEdge_v.1/
Columns: material_id, formula, cif_structure, description, band_gap, volume, is_gap_direct
Input = description (text). Outputs = band_gap, volume, is_gap_direct.

## Day 2 results - data exploration
Rows: train 125098, validation 9945, test 11531 - paper says test 9888.
Train has 33 rows with missing volume and is_gap_direct - drop them.
About half of crystals have band gap 0. Direct gap is only about 14 percent of rows.
Median description is 224 words. About 29 percent are over 400 words. Longest is 9825.
