# Preprocessing Notes — Day 2

Source: `data/raw/system_logs_dataset.csv` (100,000 rows, 63 columns)
Script: `scripts/preprocess.py`

## 1. Columns dropped from X
| Column | Reason |
|---|---|
| `is_attack` | Target variable — split out as `y`, not part of `X` |
| `attack_name` | Target leakage (only populated for attack rows; also mostly null) |
| `timestamp` | Raw epoch timestamp isn't a direct measurement; dropped for this pass |

## 2. Categorical encoding
- `disk` has 3 nominal values (`sda1`, `sda2`, `sda5`) — no inherent order, so **one-hot encoded** via `pd.get_dummies` into `disk_sda1`, `disk_sda2`, `disk_sda5` rather than label-encoded, to avoid implying a false ordinal relationship.

## 3. Train/test split
- 80/20 **stratified** split on `is_attack`, `random_state=42`.
- Done *before* scaling, so the scaler is fit only on training data (no leakage).
- Class balance preserved in both splits: 90% class 0 / 10% class 1.

## 4. Scaling
- **StandardScaler** (zero mean, unit variance) chosen over MinMaxScaler because most of these system-metric features (CPU load, latency, throughput, etc.) are roughly continuous with outliers/spikes rather than bounded ranges — standardization is less distorted by extreme values than min-max scaling.
- Fit on `X_train` only; same fitted scaler applied to `X_test`.
- One-hot `disk_*` columns (already 0/1) were left unscaled.
- All other 61 numeric columns were scaled.

## 5. Class imbalance strategy
- Class balance is 90/10 (moderate, not extreme) — **class weighting** (`class_weight='balanced'` or equivalent) is the planned approach per model, applied at training time.
- SMOTE was considered but not used by default; if a model underperforms with class weighting alone, SMOTE can be applied to the training set only (never to `X_test`/`y_test`).
- This should be cross-checked against Siya's class-balance numbers before finalizing — the 90/10 split observed here matches `results/data_summary.md`.

## 6. Outputs
Saved to `data/processed/`:
- `X_train.csv` (80,000 × 62)
- `X_test.csv` (20,000 × 62)
- `y_train.csv`, `y_test.csv`

62 feature columns total: 63 raw columns − 3 dropped (`is_attack`, `attack_name`, `timestamp`) − 1 (`disk` replaced) + 3 (`disk_sda1`, `disk_sda2`, `disk_sda5`) = 62.

**Note:** `pd.get_dummies` was used without `drop_first=True`, so all 3 `disk_*` dummies are present. If a linear/logistic model is used later, consider `drop_first=True` to avoid the dummy-variable trap; tree-based models are unaffected either way.
