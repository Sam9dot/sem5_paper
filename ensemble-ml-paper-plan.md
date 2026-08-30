# MTDS Attack Detection — Ensemble ML Paper: Work Plan

**Team:** Siya, Shriya, Ruchit
**Duration:** 7 days
**Deliverable:** A paper training 10 individual ML models on the system-logs dataset, combining the best into an ensemble, and reporting results — following the format of the lab's prior "Objective 1" papers (meta-ensemble / stacked anomaly detector / weighted ensemble series).

**Target:** `is_attack` (binary: 0 = normal, 1 = attack) as the classification label. `attack_name` is available for later multi-class analysis if time allows, but is out of scope for the core deliverable — do not let this expand.

---

## 0. Before Day 1 — 15-minute team sync (do this today)

- [ ] Confirm binary classification (`is_attack`) is the target — not multi-class `attack_name`. If your guide wants multi-class, this whole plan needs to change, so confirm first.
- [ ] Agree on a shared folder (Google Drive / GitHub repo) with subfolders: `/data`, `/notebooks`, `/results`, `/paper`.
- [ ] Agree on train/test split method: **80/20, stratified by `is_attack`**, fixed `random_state=42` for everyone — this is non-negotiable, because if each person splits differently, results aren't comparable.
- [ ] Agree on the exact CSV file everyone uses (`Dataset 2 system logs dataset.csv`) and confirm no one is working off a stale copy.
- [ ] Set up a shared results spreadsheet (Google Sheet) with columns: `Model | Owner | Accuracy | Precision | Recall | F1 | ROC-AUC | Notes` — every model owner fills their row(s) here as they finish.

---

## Phase 1 — Data Understanding & Preprocessing (Day 1)

Split into three parallel sub-tasks so no one is idle waiting on another. Whoever finishes preprocessing (Ruchit, below) produces the **single cleaned train/test CSV pair** that Siya and Shriya both load for Phase 2 — this is the one file everyone must be using the same version of.

### Siya — Data Loading & Class Balance Analysis
- [ ] Load the CSV, report total row count and column count.
- [ ] Compute `is_attack` class distribution (count and %) — expect heavy imbalance based on prior papers in this series.
- [ ] Check for nulls/missing values per column, decide and document how each will be handled (drop column, impute, etc.).
- [ ] Check for duplicate rows.
- [ ] Identify non-numeric / non-feature columns to exclude from model input: `timestamp`, `disk` (categorical, e.g. `sda1`/`sda2`), `attack_name` (label leakage if included as a feature — must be dropped for the binary task).
- [ ] Write a short `data_summary.md` (row/col counts, class balance %, null-handling decisions, dropped columns) and share with the team.

### Shriya — Exploratory Data Analysis (EDA)
- [ ] Plot distributions of 5–8 key features (e.g. `CPU (%)`, `network_bandwidth`, `network_latency`, `firewall_packets_dropped`, `TCP Connection Count`) split by `is_attack` = 0 vs 1 — look for features that visibly separate the two classes.
- [ ] Compute a correlation matrix / heatmap across numeric features to flag redundant features (e.g. two columns that are near-duplicates of each other).
- [ ] Identify outliers per feature (boxplots or IQR method) and note whether they look like real attack signals or data errors.
- [ ] Summarize the top 8–10 features that look most predictive of `is_attack` — this feeds directly into the paper's "Feature Analysis" subsection later.
- [ ] Save all plots to `/results/eda/` with clear filenames.

### Ruchit — Feature Engineering & Preprocessing Pipeline
- [ ] Build the preprocessing pipeline: encode categorical columns (`disk`), scale numeric features (StandardScaler or MinMaxScaler — pick one, document why).
- [ ] Perform the 80/20 stratified train/test split using the agreed `random_state=42`.
- [ ] Save `X_train.csv`, `X_test.csv`, `y_train.csv`, `y_test.csv` (or a single pickled pipeline + splits) to `/data/processed/` and share with the team.
- [ ] Document the exact preprocessing steps in `preprocessing_notes.md` so Methodology section can be written directly from it later.
- [ ] Decide and document the class-imbalance strategy (e.g. class weighting in each model, or SMOTE on training data only — never on test data). Confirm this with Siya's class-balance numbers first.

**End-of-day sync:** 10-minute call to confirm the processed dataset is ready and everyone can load it before Day 2 starts.

---

## Phase 2 — Individual Model Training (Days 2–3)

10 models split evenly, ~3–4 each. Each person trains their models **on the exact same processed train/test split** from Phase 1.

### Siya — 4 models
1. Logistic Regression
2. Random Forest
3. XGBoost
4. K-Nearest Neighbors (KNN)

### Shriya — 3 models
1. Decision Tree
2. Support Vector Machine (SVM)
3. Naive Bayes

### Ruchit — 3 models
1. Gradient Boosting (e.g. GradientBoostingClassifier / LightGBM)
2. AdaBoost
3. Multi-Layer Perceptron / ANN

### Day 2 — Baseline runs (everyone, in parallel)
- [ ] Train each assigned model with default/sane hyperparameters first — goal is a working number today, not a perfect one.
- [ ] For each model, compute: Accuracy, Precision, Recall, F1-score, ROC-AUC, and the confusion matrix.
- [ ] Log every result into the shared results spreadsheet immediately after running — don't batch this for later.
- [ ] Flag to the team if any model's `precision`/`recall` for the attack class is near 0 despite high accuracy — this is the class-imbalance trap and needs fixing before Day 3, not after.

### Day 3 — Tuning (everyone, in parallel)
- [ ] Light hyperparameter tuning per model — 2–3 key parameters each, via `GridSearchCV` or `RandomizedSearchCV` with 3–5 fold cross-validation. Don't over-invest time here; the ensemble is what really matters.
  - Logistic Regression: `C`, `class_weight`
  - Random Forest: `n_estimators`, `max_depth`, `class_weight`
  - XGBoost: `n_estimators`, `max_depth`, `scale_pos_weight`
  - KNN: `n_neighbors`, `weights`
  - Decision Tree: `max_depth`, `min_samples_split`, `class_weight`
  - SVM: `C`, `kernel`
  - Naive Bayes: variant choice (Gaussian vs Bernoulli), minimal tuning needed
  - Gradient Boosting: `n_estimators`, `learning_rate`, `max_depth`
  - AdaBoost: `n_estimators`, `learning_rate`
  - MLP: hidden layer sizes, `alpha`, `max_iter`
- [ ] Re-run final metrics after tuning and update the shared spreadsheet (mark old rows as "baseline", new ones as "tuned").
- [ ] Save each trained model object (pickle/joblib) to `/results/models/` — the ensemble step needs to load these directly, not retrain them.
- [ ] Save each model's predicted probabilities on the test set (not just class labels) to `/results/predictions/` — required for weighted averaging / soft voting in Phase 3.

**End-of-day sync:** Everyone shares their final metrics table row. Team collectively identifies the top 3–5 performing models by F1-score (not accuracy) — these move on to Phase 3.

---

## Phase 3 — Ensemble Model (Day 4)

**Owner: Ruchit** (builds and runs the ensemble), with Siya and Shriya providing their saved model predictions from Phase 2.

- [ ] Ruchit collects the saved predicted-probability files from all 3 team members for the top 3–5 models (by F1-score).
- [ ] Build **majority voting** ensemble across the top models — simplest, matches the lab's prior papers, easy to justify in the write-up.
- [ ] Build **weighted averaging** ensemble — weight each model's vote by its individual F1-score or another metric — matches Objective 1 Paper 3's approach directly.
- [ ] (Stretch goal, only if time allows) Try a **stacking** ensemble with a simple meta-learner (e.g. Logistic Regression) on top of the base models' predictions.
- [ ] Evaluate every ensemble variant with the same metrics (Accuracy, Precision, Recall, F1, ROC-AUC, confusion matrix) on the same held-out test set.
- [ ] Confirm the best ensemble beats the best individual model on F1/Recall — if it doesn't, flag this immediately to Siya and Shriya so the team can debug together (bad weighting, wrong models selected, etc.) rather than losing a day later.
- [ ] Log final ensemble results into the shared spreadsheet.

**Siya & Shriya on Day 4 (parallel, not idle):**
- [ ] Siya: start building the final results comparison table (all 10 models + ensemble variants) and draft 1–2 comparison bar charts (F1 and Recall by model).
- [ ] Shriya: start drafting the Related Work section (see Phase 5) using the 5 existing Objective 1 papers, since this doesn't depend on final ensemble numbers.

---

## Phase 4 — Results Compilation (Day 5)

Shared task, ~2–3 hours each.

- [ ] Finalize the master results table: 10 individual models + all ensemble variants, all 5 metrics, sorted by F1-score.
- [ ] Finalize charts: bar chart comparing F1/Recall across all models + ensemble; confusion matrix heatmaps for the best individual model and the best ensemble side by side.
- [ ] Write a short "Feature Importance" note if any of the tree-based models (Random Forest, XGBoost, Gradient Boosting) expose feature importances — tie this back to Shriya's Day 1 EDA findings on which features looked predictive.
- [ ] Everyone reviews the full results table together and agrees on the final headline number (e.g. "our ensemble achieves X% F1, a Y-point improvement over the best individual model") — this becomes the paper's core claim.

---

## Phase 5 — Paper Writing (Day 6)

Split by section, written in parallel, using the existing Objective 1 papers as a structural template (same lab, same format expected).

### Siya — Introduction + Abstract
- [ ] Motivate the problem: MTDS security, side-channel/system-level attack detection, why ensembles help.
- [ ] Summarize the paper's contribution in 3–4 sentences (10 models compared, ensemble proposed, X% improvement).
- [ ] Write the Abstract last, after Methodology/Results sections exist, so it accurately reflects final numbers.

### Shriya — Related Work + Dataset Description
- [ ] Related Work: summarize the 5 prior Objective 1 papers (meta-ensemble classifier, stacked anomaly detector, weighted averaging + majority voting, OpenStack comparison, Gaussian models) — 1 short paragraph each, then a sentence on how this paper differs (broader model comparison, this specific dataset).
- [ ] Dataset Description: row/column counts, feature categories (CPU/memory/network/disk/firewall metrics), class balance, and how the train/test split was done — pull directly from Siya's Day 1 `data_summary.md` and Ruchit's `preprocessing_notes.md`.

### Ruchit — Methodology + Results + Conclusion
- [ ] Methodology: list all 10 models with a one-line description of each, the tuning approach (Day 3), and the ensemble method(s) used (Day 4) — pull directly from Phase 2/3 notes.
- [ ] Results: present the master table and charts from Phase 4, with 2–3 sentences interpreting the key finding (which single models did best, why the ensemble improved on them).
- [ ] Conclusion: summarize the finding, note limitations (e.g. single dataset, binary-only classification), suggest future work (multi-class on `attack_name`, deep learning ensemble, testing on other datasets — matches the "future work" tone of the prior papers).

**Everyone:** keep sections to the length used in the prior papers (they're all 5–10 pages) — don't over-write.

---

## Phase 6 — Merge, Polish, Submit (Day 7)

Shared task.

- [ ] Merge all sections into one document in order: Abstract → Introduction → Related Work → Dataset → Methodology → Results → Conclusion → References.
- [ ] Format to match the target venue/journal's template (check what Objective 1 Paper 3/4 used, since this is likely the same target).
- [ ] Build the References section — include the 5 Objective 1 papers as citations, plus any external sources cited in Related Work.
- [ ] Full team read-through: check that every number quoted in the text matches the results table exactly.
- [ ] Proofread pass — one person reads the whole thing aloud or line-by-line for typos/flow.
- [ ] Buffer time built into this day for any model rerun or number mismatch found during review.
- [ ] Submit.

---

## Quick Reference — Who Owns What

| Area | Owner | Support |
|---|---|---|
| Data loading & class balance | Siya | — |
| EDA | Shriya | — |
| Preprocessing pipeline & split | Ruchit | — |
| Models: LogReg, RF, XGBoost, KNN | Siya | — |
| Models: Decision Tree, SVM, Naive Bayes | Shriya | — |
| Models: Gradient Boosting, AdaBoost, MLP | Ruchit | — |
| Ensemble build & evaluation | Ruchit | Siya, Shriya (provide predictions) |
| Results table & charts | Siya | — |
| Introduction + Abstract | Siya | — |
| Related Work + Dataset Description | Shriya | — |
| Methodology + Results + Conclusion | Ruchit | — |
| Final merge & polish | All 3 | — |

**Golden rule:** every model must be evaluated on the exact same train/test split (from Ruchit's Day 1 pipeline) and every result goes into the shared spreadsheet the moment it's ready — not at end of day, not from memory.
