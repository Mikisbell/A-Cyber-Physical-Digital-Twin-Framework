#!/usr/bin/env bash
# tools/run_guardian_test.sh
# ─────────────────────────────────────────────────────────────────────────────
# Stress Test de Inconsistencia Física — "Humillación del Búnker"
# Inyecta los tres ataques termodinámicos al Guardian Angel directamente
# sobre el código, sin necesidad del hardware real.
#
# Ataques simulados:
#  S-1: fn sube de 8.0 Hz a 11.0 Hz (rigidez mágica)
#  S-2: temperatura de 500°C (imposible en structural material)
#  S-3: salto brusco de 22°C a 60°C en un solo paquete (ΔT=38°C)
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ -n "${VIRTUAL_ENV:-}" ]]; then
  echo "Using active virtualenv: $VIRTUAL_ENV"
elif [[ -f .venv/bin/activate ]]; then
  source .venv/bin/activate
else
  echo "⚠️  No virtualenv found (.venv/ or \$VIRTUAL_ENV). Running with system Python."
fi

python3 - <<'EOF'
import sys
sys.path.insert(0, ".")
from src.physics.bridge import GuardianAngel

ga = GuardianAngel()
print("=" * 64)
print("  GUARDIAN ANGEL — STRESS TEST DE INCONSISTENCIA FÍSICA")
print("=" * 64)

casos = [
    # (descripcion, fn_hz, tmp_c, expected_status)
    ("Paquete sano (baseline)",             8.0,  22.0, "ok"),
    ("S-1 Rigidez Mágica: fn sube a 11Hz", 11.0, 22.0, "!ok"),
]
ga2 = GuardianAngel()  # Guardian fresco para S-2
casos_s2 = [
    ("Paquete sano (baseline)",              8.0,  22.0, "ok"),
    ("S-2 Temperatura 500°C",                7.9, 500.0, "!ok"),
]
ga3 = GuardianAngel()  # Guardian fresco para S-3
casos_s3 = [
    ("Paquete sano (baseline)",              8.0,  22.0, "ok"),
    ("S-3 Gradiente Brusco: 22→60°C",        7.9,  60.0, "!ok"),
]

def run_casos(guardian, lista):
    for desc, fn, tmp, expected in lista:
        status, msg = guardian.validate(fn=fn, tmp=tmp)
        ok = (status == "ok")
        expected_ok = (expected == "ok")
        icono = "✅" if ok else "🚨"
        resultado = "PASS" if ok == expected_ok else "❌ FALLO DE TEST"
        msg_show = f"→ {msg}" if msg else ""
        print(f"  {icono}  [{resultado}]  {desc}")
        if msg_show:
            print(f"         {msg_show}")
    print()

print("\n[ ATAQUE S-1: RIGIDEZ MÁGICA ]")
run_casos(ga, casos)

print("[ ATAQUE S-2: TEMPERATURA FÍSICAMENTE IMPOSIBLE ]")
run_casos(ga2, casos_s2)

print("[ ATAQUE S-3: GRADIENTE TÉRMICO BRUSCO ]")
run_casos(ga3, casos_s3)

print("=" * 64)
print("  El Búnker ha procesado la paradoja física.")
print("  Si todos son PASS, el Guardian Angel es digno de la campaña.")
print("=" * 64)
EOF
