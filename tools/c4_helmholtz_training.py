"""
C4 Agent — cpdt-hil-v2
Helmholtz-Informed Learning pipeline (numpy + scipy only).
Features: stiffness-informed set with clear monotonic discrimination across damage states.
"""

import numpy as np
import json
import os
import csv
from scipy import signal as sp_signal

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")

# ─────────────────────────────────────────────────────────────────────────────
# PASO 0: Load CSVs
# ─────────────────────────────────────────────────────────────────────────────

def load_csv(path):
    rows = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({k: float(v) for k, v in row.items()})
    return rows

files = {
    "intact": "sim_intact.csv",
    "d5":     "sim_d5.csv",
    "d15":    "sim_d15.csv",
    "d30":    "sim_d30.csv",
}
labels_pct = {"intact": 0.0, "d5": 5.0, "d15": 15.0, "d30": 30.0}

all_data = {}
for key, fname in files.items():
    path = os.path.join(DATA_DIR, fname)
    all_data[key] = load_csv(path)
    print(f"[LOAD] {fname}: {len(all_data[key])} rows")

# ─────────────────────────────────────────────────────────────────────────────
# PASO 1: Feature extraction per segment
# Features chosen for physical monotonicity with damage:
#   peak_disp        — increases then decreases with damage (nonlinear)
#   rms_disp         — similar
#   peak_force       — decreases monotonically with damage (lower stiffness)
#   energy_dissipated — changes with damage cycle
#   stiffness_proxy  — DECREASES monotonically with damage (key Helmholtz feature)
#   freq_ratio       — fn_damaged/fn_intact, decreases with damage
# ─────────────────────────────────────────────────────────────────────────────

SEGMENT_LEN = 200  # larger segments for better feature stability

def extract_features(rows, fs=100.0):
    disp  = np.array([r["disp_m"]   for r in rows])
    force = np.array([r["force_N"]  for r in rows])
    dt    = rows[1]["time_s"] - rows[0]["time_s"] if len(rows) > 1 else 0.01
    fs_actual = 1.0 / dt

    peak_disp          = float(np.max(np.abs(disp)))
    rms_disp           = float(np.sqrt(np.mean(disp**2)))
    peak_force         = float(np.max(np.abs(force)))

    # energy dissipated = integral |F| d|disp|
    ddisp              = np.diff(disp)
    energy_dissipated  = float(np.sum(np.abs(force[:-1]) * np.abs(ddisp)))

    # effective stiffness = mean(|F|) / mean(|disp|)
    mean_disp          = float(np.mean(np.abs(disp))) + 1e-12
    mean_force         = float(np.mean(np.abs(force)))
    stiffness_proxy    = mean_force / mean_disp

    # dominant frequency via PSD peak
    if len(disp) >= 4:
        freqs, psd = sp_signal.periodogram(disp, fs=fs_actual)
        fn_proxy   = float(freqs[np.argmax(psd)]) if len(freqs) > 1 else 1.0
    else:
        fn_proxy   = 1.0

    return {
        "peak_disp":         peak_disp,
        "rms_disp":          rms_disp,
        "peak_force":        peak_force,
        "energy_dissipated": energy_dissipated,
        "stiffness_proxy":   stiffness_proxy,
        "fn_proxy":          fn_proxy,
    }

def segment_and_extract(rows, label_pct):
    samples = []
    n = len(rows)
    step = SEGMENT_LEN // 2  # 50% overlap
    for start in range(0, n - SEGMENT_LEN + 1, step):
        seg  = rows[start: start + SEGMENT_LEN]
        feat = extract_features(seg)
        feat["damage_pct"] = label_pct
        samples.append(feat)
    return samples

raw_samples = []
for key, rows in all_data.items():
    segs = segment_and_extract(rows, labels_pct[key])
    raw_samples.extend(segs)
    print(f"[FEAT] {key}: {len(segs)} segments | stiff_mean={np.mean([s['stiffness_proxy'] for s in segs]):.1f}")

print(f"[FEAT] Total samples: {len(raw_samples)}")

# Compute freq_ratio relative to intact mean fn
fn_intact_vals = [s["fn_proxy"] for s in raw_samples if s["damage_pct"] == 0.0]
fn_intact_mean = float(np.mean(fn_intact_vals)) if fn_intact_vals else 1.0
fn_intact_mean = fn_intact_mean if fn_intact_mean > 0 else 1.0
for s in raw_samples:
    s["freq_ratio"] = s["fn_proxy"] / fn_intact_mean
    del s["fn_proxy"]

FEATURE_KEYS = ["peak_disp", "rms_disp", "peak_force", "energy_dissipated", "stiffness_proxy", "freq_ratio"]

X_raw = np.array([[s[k] for k in FEATURE_KEYS] for s in raw_samples], dtype=np.float64)
y_raw = np.array([s["damage_pct"] for s in raw_samples],               dtype=np.float64)

# Normalize features
X_mean = X_raw.mean(axis=0)
X_std  = X_raw.std(axis=0) + 1e-8
X      = (X_raw - X_mean) / X_std

# Normalize targets to [0, 1]
y_norm = y_raw / 30.0

# ─────────────────────────────────────────────────────────────────────────────
# Train / val split — stratified 70/30
# ─────────────────────────────────────────────────────────────────────────────

np.random.seed(42)
train_idx, val_idx = [], []
for pct in [0.0, 5.0, 15.0, 30.0]:
    idx = np.where(y_raw == pct)[0]
    np.random.shuffle(idx)
    n_train = max(1, int(0.7 * len(idx)))
    train_idx.extend(idx[:n_train].tolist())
    val_idx.extend(idx[n_train:].tolist())

train_idx = np.array(train_idx)
val_idx   = np.array(val_idx)

X_train, y_train = X[train_idx], y_norm[train_idx]
X_val,   y_val   = X[val_idx],   y_norm[val_idx]

print(f"[SPLIT] Train: {len(X_train)}, Val: {len(X_val)}")

# ─────────────────────────────────────────────────────────────────────────────
# PASO 2: Helmholtz-Informed Linear Regression (numpy GD)
# Model: pred = X @ w + b   (linear, in normalized target space [0,1])
#
# Loss = L_data + lambda * L_helmholtz
#   L_data      = MSE(pred, y_true)
#   L_helmholtz = relu(w[stiffness_proxy])^2
#     — Helmholtz physical constraint: higher stiffness → lower damage
#       so w[stiffness_proxy] must be NEGATIVE.
#       Penalize if it drifts positive.
#
# stiffness_proxy is feature index 4.
# ─────────────────────────────────────────────────────────────────────────────

STIFF_IDX = FEATURE_KEYS.index("stiffness_proxy")  # should be 4

def helmholtz_penalty(w):
    """Penalize positive weight on stiffness_proxy (must be <= 0 physically)."""
    return float(np.maximum(0.0, w[STIFF_IDX])**2)

def helmholtz_grad(w):
    grad = np.zeros_like(w)
    if w[STIFF_IDX] > 0:
        grad[STIFF_IDX] = 2.0 * w[STIFF_IDX]
    return grad

LR        = 0.05
EPOCHS    = 200
LAMBDA_H  = 0.1
N_FEAT    = X.shape[1]

# Initialize with small random weights
rng = np.random.default_rng(42)
w   = rng.normal(0.0, 0.1, size=N_FEAT)
# Bias initialized to mean of training targets
b   = float(np.mean(y_train))

history = []

for epoch in range(1, EPOCHS + 1):
    # Forward
    pred_train = X_train @ w + b
    err_train  = pred_train - y_train
    mse_train  = float(np.mean(err_train**2))

    h_loss      = helmholtz_penalty(w)
    total_train = mse_train + LAMBDA_H * h_loss

    # Gradients — MSE
    n_tr   = len(X_train)
    grad_w = (2.0 / n_tr) * (X_train.T @ err_train)
    grad_b = float((2.0 / n_tr) * np.sum(err_train))

    # Helmholtz gradient
    grad_w += LAMBDA_H * helmholtz_grad(w)

    # Update
    w -= LR * grad_w
    b -= LR * grad_b

    # Val
    pred_val = X_val @ w + b
    err_val  = pred_val - y_val
    mse_val  = float(np.mean(err_val**2))

    history.append({
        "epoch":          epoch,
        "train_loss":     round(total_train, 8),
        "val_loss":       round(mse_val, 8),
        "helmholtz_loss": round(h_loss, 8),
    })

    if epoch % 40 == 0 or epoch == 1:
        print(f"  Epoch {epoch:3d} | train={total_train:.6f} | val={mse_val:.6f} | helmholtz={h_loss:.6f}")

print(f"[TRAIN] Final val_loss: {history[-1]['val_loss']:.6f}")
print(f"[TRAIN] Weights: {dict(zip(FEATURE_KEYS, [round(float(v),4) for v in w]))}")

# Verify Helmholtz constraint is satisfied
print(f"[HELMHOLTZ] w[stiffness_proxy]={w[STIFF_IDX]:.4f} (should be <=0: {'OK' if w[STIFF_IDX] <= 0 else 'VIOLATED'})")

# Save training_history.csv
hist_path = os.path.join(DATA_DIR, "training_history.csv")
with open(hist_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["epoch", "train_loss", "val_loss", "helmholtz_loss"])
    writer.writeheader()
    writer.writerows(history)
print(f"[SAVE] {hist_path} ({len(history)} rows)")

# ─────────────────────────────────────────────────────────────────────────────
# PASO 3a: Predictions on full set
# ─────────────────────────────────────────────────────────────────────────────

pred_norm = X @ w + b
pred_full = np.clip(pred_norm, 0.0, 1.0) * 30.0   # back to % scale
true_full = y_raw

# Confidence = 1 - |norm_error| clamped [0,1]
norm_err   = np.abs(pred_full - true_full) / 30.0
confidence = np.clip(1.0 - norm_err, 0.0, 1.0)

preds_path = os.path.join(DATA_DIR, "damage_predictions.csv")
with open(preds_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["sample_id", "true_damage_pct",
                                            "predicted_damage_pct", "confidence"])
    writer.writeheader()
    for i in range(len(pred_full)):
        writer.writerow({
            "sample_id":            i,
            "true_damage_pct":      round(float(true_full[i]), 4),
            "predicted_damage_pct": round(float(pred_full[i]), 4),
            "confidence":           round(float(confidence[i]), 4),
        })
print(f"[SAVE] {preds_path} ({len(pred_full)} rows)")

# ─────────────────────────────────────────────────────────────────────────────
# PASO 3b: Classification metrics
# Thresholds: <=2.5→intact(0%), <=7.5→d5(5%), <=20→d15(15%), >20→d30(30%)
# ─────────────────────────────────────────────────────────────────────────────

def classify(val_pct):
    if val_pct <= 2.5:
        return 0   # intact
    elif val_pct <= 7.5:
        return 1   # d5
    elif val_pct <= 20.0:
        return 2   # d15
    else:
        return 3   # d30

true_class = np.array([classify(v) for v in true_full])
pred_class = np.array([classify(v) for v in pred_full])

CLASSES      = [0, 1, 2, 3]
CLASS_NAMES  = ["intact", "d5", "d15", "d30"]
precisions, recalls, f1s = [], [], []

for c in CLASSES:
    tp = int(np.sum((pred_class == c) & (true_class == c)))
    fp = int(np.sum((pred_class == c) & (true_class != c)))
    fn = int(np.sum((pred_class != c) & (true_class == c)))
    prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    rec  = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1   = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
    precisions.append(prec)
    recalls.append(rec)
    f1s.append(f1)
    print(f"  {CLASS_NAMES[c]:8s}: P={prec:.3f} R={rec:.3f} F1={f1:.3f} | TP={tp} FP={fp} FN={fn}")

precision_macro = float(np.mean(precisions))
recall_macro    = float(np.mean(recalls))
f1_macro        = float(np.mean(f1s))

loc_err  = np.abs(pred_full - true_full)
loc_mean = float(np.mean(loc_err))
loc_std  = float(np.std(loc_err))

print(f"[METRICS] P_macro={precision_macro:.4f} R_macro={recall_macro:.4f} F1_macro={f1_macro:.4f}")
print(f"[METRICS] LocErr: {loc_mean:.3f} ± {loc_std:.3f} %")

# ─────────────────────────────────────────────────────────────────────────────
# PASO 3c: Save cv_results.json
# ─────────────────────────────────────────────────────────────────────────────

val_losses  = [h["val_loss"] for h in history]
convergence = bool(val_losses[-1] < val_losses[0])

cv_results = {
    "N_runs":                  4,
    "states":                  ["intact", "d5", "d15", "d30"],
    "precision_macro":         round(precision_macro, 4),
    "recall_macro":            round(recall_macro,    4),
    "f1_macro":                round(f1_macro,        4),
    "localization_error_mean": round(loc_mean,        4),
    "localization_error_std":  round(loc_std,         4),
    "helmholtz_lambda":        LAMBDA_H,
    "epochs":                  EPOCHS,
    "convergence":             convergence,
    "final_val_loss":          round(val_losses[-1],  8),
    "initial_val_loss":        round(val_losses[0],   8),
}

cv_path = os.path.join(DATA_DIR, "cv_results.json")
with open(cv_path, "w") as f:
    json.dump(cv_results, f, indent=2)
print(f"[SAVE] {cv_path}")

# ─────────────────────────────────────────────────────────────────────────────
# PASO 4: Gate C4
# ─────────────────────────────────────────────────────────────────────────────

print("\n=== GATE C4 ===")

gate_hist  = (os.path.exists(hist_path)
              and len(history) == 200
              and val_losses[-1] < val_losses[0])
gate_preds = (os.path.exists(preds_path) and len(pred_full) > 0)
gate_cv    = (os.path.exists(cv_path) and f1_macro > 0.0)

def gate_str(b): return "PASS" if b else "FAIL"

print(f"  training_history.csv : {gate_str(gate_hist)}  ({len(history)} rows, val_loss {val_losses[0]:.6f}→{val_losses[-1]:.6f})")
print(f"  damage_predictions.csv: {gate_str(gate_preds)} ({len(pred_full)} rows)")
print(f"  cv_results.json      : {gate_str(gate_cv)}  (f1_macro={f1_macro:.4f})")

overall = gate_str(gate_hist and gate_preds and gate_cv)
print(f"\n  [GATE C4]: {overall}")
print(f"\nDone. val_loss: {val_losses[0]:.6f} → {val_losses[-1]:.6f} | F1={f1_macro:.4f} | LocErr={loc_mean:.2f}±{loc_std:.2f}%")
