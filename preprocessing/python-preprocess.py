"""
Feature engineering & preprocessing pipeline — sem5_paper
Ruchit's Day 2 deliverable.

Steps:
1. Load raw CSV
2. Drop target/leakage/raw-timestamp columns from X
3. One-hot encode `disk` (nominal, 3 categories)
4. Stratified 80/20 train/test split (random_state=42)
5. Scale numeric features with StandardScaler, fit on train only
6. Save X_train/X_test/y_train/y_test to data/processed/
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from pathlib import Path

RAW_PATH = Path("data/raw/system_logs_dataset.csv")
OUT_DIR = Path("data/processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 42
TEST_SIZE = 0.2

df = pd.read_csv(RAW_PATH)

# --- 1. Split target / drop leakage & raw timestamp ---
y = df["is_attack"]
X = df.drop(columns=["is_attack", "attack_name", "timestamp"])

# --- 2. One-hot encode categorical `disk` ---
X = pd.get_dummies(X, columns=["disk"], prefix="disk")

# --- 3. Stratified train/test split (before scaling, to avoid leakage) ---
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=TEST_SIZE,
    stratify=y,
    random_state=RANDOM_STATE,
)

# --- 4. Scale numeric features (fit on train only) ---
numeric_cols = X_train.select_dtypes(include=["int64", "float64"]).columns.tolist()
# one-hot disk_* columns are 0/1 already — leave them unscaled
numeric_cols = [c for c in numeric_cols if not c.startswith("disk_")]

X_train[numeric_cols] = X_train[numeric_cols].astype("float64")
X_test[numeric_cols] = X_test[numeric_cols].astype("float64")

scaler = StandardScaler()
X_train.loc[:, numeric_cols] = scaler.fit_transform(X_train[numeric_cols])
X_test.loc[:, numeric_cols] = scaler.transform(X_test[numeric_cols])

# --- 5. Save splits ---
X_train.to_csv(OUT_DIR / "X_train.csv", index=False)
X_test.to_csv(OUT_DIR / "X_test.csv", index=False)
y_train.to_csv(OUT_DIR / "y_train.csv", index=False)
y_test.to_csv(OUT_DIR / "y_test.csv", index=False)

print("Shapes:")
print("  X_train:", X_train.shape, " X_test:", X_test.shape)
print("  y_train class balance:\n", y_train.value_counts(normalize=True))
print("  y_test class balance:\n", y_test.value_counts(normalize=True))
print(f"Saved to {OUT_DIR}/")
