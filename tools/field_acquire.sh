#!/usr/bin/env bash
# ============================================================
# tools/field_acquire.sh — Belico Stack Field Data Acquisition
# ============================================================
# Automated launcher for field campaign sessions (S1-S4).
# Handles pre-checks, logging, and post-session validation.
#
# Usage:
#   ./tools/field_acquire.sh                # S1 ambient, 30min, auto-detect port
#   ./tools/field_acquire.sh --session S2 --duration 600 --port /dev/ttyUSB1
#   ./tools/field_acquire.sh --session S1 --mode usb   # Direct USB (Nano33)
#
# Requirements: python3 with belico-stack venv active
# ============================================================

set -euo pipefail

# ── Defaults ──────────────────────────────────────────────
SESSION="S1"
DURATION_S=1800       # 30 min default
PORT=""               # auto-detect
MODE="lora"           # lora | usb
SITE="La Presa del Norte"
OBSERVER=""
RESET_BASELINE=false

# ── Parse arguments ───────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --session)    SESSION="$2";        shift 2 ;;
        --duration)   DURATION_S="$2";     shift 2 ;;
        --port)       PORT="$2";           shift 2 ;;
        --mode)       MODE="$2";           shift 2 ;;
        --site)       SITE="$2";           shift 2 ;;
        --observer)   OBSERVER="$2";       shift 2 ;;
        --reset-baseline) RESET_BASELINE=true; shift ;;
        -h|--help)
            echo "Usage: $0 [--session S1|S2|S3|S4] [--duration SECS] [--port /dev/ttyX] [--mode lora|usb]"
            exit 0 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# ── Paths ─────────────────────────────────────────────────
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

DATE_TAG=$(date +%Y%m%d_%H%M%S)
RAW_CSV="data/raw/field_${SESSION}_${DATE_TAG}.csv"
META_YAML="data/raw/field_${SESSION}_${DATE_TAG}_meta.yaml"
LOG_FILE="data/raw/field_${SESSION}_${DATE_TAG}.log"

# ── Auto-detect serial port ──────────────────────────────
if [[ -z "$PORT" ]]; then
    if ls /dev/ttyUSB* 2>/dev/null | head -1 > /dev/null; then
        PORT=$(ls /dev/ttyUSB* 2>/dev/null | head -1)
    elif ls /dev/ttyACM* 2>/dev/null | head -1 > /dev/null; then
        PORT=$(ls /dev/ttyACM* 2>/dev/null | head -1)
    else
        echo "[FIELD] ERROR: No serial port found. Connect sensor and retry."
        echo "[FIELD]        Or specify --port /dev/ttyXXX"
        exit 1
    fi
fi

# ── Pre-flight checks ────────────────────────────────────
echo "=============================================="
echo " BELICO STACK — FIELD DATA ACQUISITION"
echo "=============================================="
echo " Session:  $SESSION"
echo " Duration: ${DURATION_S}s ($((DURATION_S / 60))min)"
echo " Port:     $PORT"
echo " Mode:     $MODE"
echo " Site:     $SITE"
echo " Output:   $RAW_CSV"
echo "=============================================="

# Check data/raw/ exists
mkdir -p data/raw data/processed

# Check params.yaml hash matches params.h
echo "[FIELD] Pre-flight: regenerating params..."
python3 tools/generate_params.py 2>&1 | tail -1

# Check baseline exists
if [[ -f config/field_baseline.yaml ]]; then
    FN_BASE=$(grep fn_baseline_hz config/field_baseline.yaml | awk '{print $2}')
    echo "[FIELD] Baseline loaded: fn=${FN_BASE} Hz ($(grep site config/field_baseline.yaml | cut -d: -f2 | xargs))"
else
    echo "[FIELD] WARNING: No field_baseline.yaml — Guardian Angel will calibrate from first packet"
fi

# Check disk space
AVAIL_MB=$(df -m "$PROJECT_ROOT/data" | tail -1 | awk '{print $4}')
if [[ "$AVAIL_MB" -lt 500 ]]; then
    echo "[FIELD] WARNING: Only ${AVAIL_MB}MB free. Recommend >500MB for 30min session."
fi

# Check port accessible
if [[ ! -e "$PORT" ]]; then
    echo "[FIELD] ERROR: Port $PORT does not exist."
    exit 1
fi

echo ""
echo "[FIELD] Starting acquisition in 5 seconds..."
echo "[FIELD] Press Ctrl+C to abort before start."
sleep 5

# ── Generate metadata file ───────────────────────────────
CONFIG_HASH=$(python3 -c "
import hashlib; from pathlib import Path
print(hashlib.sha256(Path('config/params.yaml').read_bytes()).hexdigest()[:16])
")

cat > "$META_YAML" << EOF
session: $SESSION
date: $(date +%Y-%m-%d)
time_start: "$(date +%H:%M:%S)"
time_end: ""
duration_target_s: $DURATION_S
site: "$SITE"
gps: ""
element: ""
material: "C&DW"
node_id: ""
firmware: "$(if [[ $MODE == "usb" ]]; then echo 'nano33_belico.ino'; else echo 'nicla_edge_field.ino'; fi)"
config_hash: "$CONFIG_HASH"
mode: "$MODE"
port: "$PORT"
weather:
  temperature_c:
  humidity_pct:
  wind_beaufort:
  precipitation:
  notes: ""
observer: "$OBSERVER"
EOF

echo "[FIELD] Metadata written to $META_YAML"
echo "[FIELD] ============ ACQUISITION START ============"

# ── Launch bridge with timeout ────────────────────────────
BRIDGE_ARGS="$PORT"
if [[ "$RESET_BASELINE" == true ]]; then
    BRIDGE_ARGS="$PORT --reset-baseline"
fi

# Use timeout to enforce session duration
# Bridge output goes to both terminal and log file
START_EPOCH=$(date +%s)
timeout --signal=INT "$DURATION_S" \
    python3 -u src/physics/bridge.py $BRIDGE_ARGS 2>&1 | tee "$LOG_FILE" || true

END_EPOCH=$(date +%s)
ACTUAL_DURATION=$((END_EPOCH - START_EPOCH))

echo ""
echo "[FIELD] ============ ACQUISITION END =============="
echo "[FIELD] Actual duration: ${ACTUAL_DURATION}s ($((ACTUAL_DURATION / 60))min $((ACTUAL_DURATION % 60))s)"

# Update metadata with end time
sed -i "s/^time_end: \"\"/time_end: \"$(date +%H:%M:%S)\"/" "$META_YAML"

# ── Post-session validation ──────────────────────────────
echo ""
echo "[FIELD] Post-session validation..."

# Check if bridge produced any CSV output
if [[ -f "data/processed/latest_abort.csv" ]]; then
    cp "data/processed/latest_abort.csv" "$RAW_CSV"
    echo "[FIELD] Data copied from latest_abort.csv -> $RAW_CSV"
fi

if [[ -f "$RAW_CSV" ]]; then
    python3 -c "
import pandas as pd
from pathlib import Path

csv_path = '$RAW_CSV'
df = pd.read_csv(csv_path)
n = len(df)
duration = df.iloc[-1, 0] - df.iloc[0, 0] if n > 1 else 0

print(f'[FIELD] Samples:  {n}')
print(f'[FIELD] Duration: {duration:.1f}s')

# Expected: 100Hz * duration_s
expected = $DURATION_S * 100
completeness = n / expected * 100 if expected > 0 else 0
print(f'[FIELD] Expected: ~{expected} @ 100Hz')
print(f'[FIELD] Complete: {completeness:.1f}%')

if n < 1000:
    print('[FIELD] WARNING: Very few samples. Check sensor connection.')
elif completeness < 80:
    print(f'[FIELD] WARNING: Only {completeness:.0f}% completeness. Check for gaps.')
else:
    print('[FIELD] OK: Data looks complete.')
"
else
    echo "[FIELD] WARNING: No CSV output found. Bridge may not have logged to file."
    echo "[FIELD]          Check $LOG_FILE for details."
fi

# ── Summary ──────────────────────────────────────────────
echo ""
echo "=============================================="
echo " SESSION COMPLETE"
echo "=============================================="
echo " Raw data:  $RAW_CSV"
echo " Metadata:  $META_YAML"
echo " Log:       $LOG_FILE"
echo ""
echo " Next steps:"
echo "   1. Fill GPS, element, weather in $META_YAML"
echo "   2. cp $RAW_CSV data/processed/"
echo "   3. python3 tools/plot_conference_figures.py"
echo "=============================================="
