# Data Summary — Day 1
- Rows: 100000, Columns: 63
- Class balance (is_attack): {0: np.int64(90000), 1: np.int64(10000)}
- Class balance %: {0: np.float64(90.0), 1: np.float64(10.0)}
- Duplicate rows: 0
- Columns with nulls: ['attack_name']
- Categorical column 'disk' values: ['sda2', 'sda1', 'sda5']
- Columns to drop before modeling: ['timestamp', 'attack_name']
- Null handling decision: attack_name nulls are expected (blank for normal rows) — drop column entirely, not an imputation case.
