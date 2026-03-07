#!/bin/bash
# Lanza el MOCK de LoRa y conecta el bridge al puerto virtual generado.
set -euo pipefail
cd "$(dirname "$0")/.."
trap 'kill $LORA_PID 2>/dev/null; rm -f lora_out.txt' EXIT
source .venv/bin/activate 2>/dev/null || true
export PYTHONPATH=$PWD:$PYTHONPATH

MODE=${1:-sano}
echo "📡 Lanzando Emulador LoRa en modo: $MODE"

python3 -u tools/lora_emu.py $MODE > lora_out.txt 2>&1 &
LORA_PID=$!
sleep 2

PTY_PORT=$(grep "Puerto Virtual:" lora_out.txt | awk '{print $3}')
if [ -z "$PTY_PORT" ]; then
    echo "Falla al levantar PTY LoRa."
    cat lora_out.txt
    kill $LORA_PID
    exit 1
fi

echo "🔌 Conectando bridge a $PTY_PORT..."
python3 src/physics/bridge.py $PTY_PORT

echo "🏁 Test finalizado."
