# sem5_paper

Intrusion/anomaly detection on system-log data — Semester 5 paper.

## Dataset

`data/raw/system_logs_dataset.csv` — 100,000 rows × 63 columns of system metrics (CPU, memory, disk, network, process, database, firewall counters, etc.), sampled at intervals, with a binary attack label.

- **Target:** `is_attack` (0 = normal, 1 = attack)
- **Class balance:** 90% normal / 10% attack
- **Categorical feature:** `disk` (`sda1`, `sda2`, `sda5`)
- **Excluded from features:** `attack_name` (target leakage — only populated on attack rows), `timestamp` (raw epoch, not a direct measurement)

## Project structure

```
data/
  raw/system_logs_dataset.csv     # original dataset
  processed/                      # output of the preprocessing pipeline
    X_train.csv
    X_test.csv
    y_train.csv
    y_test.csv
notebooks/
  day1_eda.ipynb                  # Day 1 exploratory data analysis
  day2_preprocessing.ipynb        # Day 2 preprocessing pipeline (notebook version)
scripts/
  preprocess.py                   # Day 2 preprocessing pipeline (script version)
results/
  data_summary.md                 # Day 1 EDA summary
  preprocessing_notes.md          # Day 2 preprocessing decisions, for Methodology section
```

## Preprocessing pipeline (Day 2)

Run either `notebooks/day2_preprocessing.ipynb` or `scripts/preprocess.py` — both implement the same pipeline; the notebook includes markdown explanations for each step, the script is the plain runnable version.

Steps:

1. **Drop leakage/non-feature columns:** `is_attack` → moved to `y`; `attack_name` and `timestamp` dropped from `X`.
2. **Null/duplicate check:** confirmed 0 nulls in features, 0 duplicate rows.
3. **Encode `disk`:** one-hot encoded (nominal, no inherent order) into `disk_sda1`, `disk_sda2`, `disk_sda5`.
4. **Outlier check — not removed:** IQR-flagged outliers in several features (`load`, `ram (GB)`, `network_errors`, `process_cpu_usage`, etc.) are ~100% attack rows. Outliers are the attack signal here, so they are deliberately **not** removed — doing so would strip out most of the minority class. See `results/preprocessing_notes.md` for the full reasoning and a commented-out safer alternative (clip outliers within the normal class only, on the training set only).
5. **Stratified 80/20 train/test split**, `random_state=42`. Done before scaling, so no test-set information leaks into the scaler.
6. **Scale numeric features:** `StandardScaler`, fit on the training set only, applied to both splits. Chosen over MinMaxScaler because these metrics have genuine spikes rather than bounded ranges. One-hot `disk_*` columns are left unscaled.
7. **Class imbalance strategy:** 90/10 imbalance — primary plan is class weighting (`class_weight='balanced'`) per model; SMOTE on the training set only as a fallback if needed. Never applied to the test set.
8. **Save outputs** to `data/processed/`: `X_train.csv` (80,000 × 62), `X_test.csv` (20,000 × 62), `y_train.csv`, `y_test.csv`.

Full write-up of each decision: [`results/preprocessing_notes.md`](results/preprocessing_notes.md).

## Requirements

```
pandas
numpy
scikit-learn
scipy
```

## Running

```bash
python scripts/preprocess.py
```

or open and run `notebooks/day2_preprocessing.ipynb` top to bottom. Paths are relative to the project root.
