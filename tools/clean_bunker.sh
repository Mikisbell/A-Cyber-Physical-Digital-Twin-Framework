#!/bin/bash
set -euo pipefail
# tools/clean_bunker.sh - Higiene Bélica: Restauración de la Arquitectura Pura
# ============================================================================
# Uso: bash tools/clean_bunker.sh [--dry-run]
# Con --dry-run solo muestra qué haría, sin ejecutar cambios.

DRY=${1:-""}

run() {
    if [ "$DRY" = "--dry-run" ]; then
        echo "  [DRY-RUN] $*"
    else
        eval "$@"
    fi
}

echo "🧹 [HIGIENE BÉLICA] Inicializando purga de residuos técnicos..."
echo ""

# ── 1. Centralizar Logs y PIDs en logs/runtime/ ──────────────────────────────
echo "📦 [PASO 1] Centralizando logs y PIDs..."
run "mkdir -p logs/runtime"

for f in *.log *_log.txt logs_*.txt dash_logs.txt battle.log; do
    [ -f "$f" ] && run "mv '$f' logs/runtime/" && echo "   → Movido: $f → logs/runtime/"
done
for f in *.pid; do
    [ -f "$f" ] && run "rm '$f'" && echo "   → Eliminado PID: $f"
done

# ── 2. Aislar Proyectos Específicos (Mantener Plantilla Universal) ─────────────
echo ""
echo "📁 [PASO 2] Verificando que no hay proyectos específicos en la plantilla..."
if ls -d */ 2>/dev/null | grep -qv -e "src/" -e "config/" -e "tools/" -e "articles/" -e "data/" -e ".agent/" -e ".agents/"; then
    echo "   ⚠️  Hay carpetas que podrían ser proyectos específicos. Revisa manualmente."
else
    echo "   → Plantilla limpia. Sin proyectos específicos detectados."
fi

# ── 3. Eliminar Scripts de Entrada Redundantes (Principio DRY) ────────────────
echo ""
echo "🔪 [PASO 3] Eliminando scripts de entrada duplicados (DRY)..."
if [ -f "setup.sh" ]; then
    run "rm setup.sh"
    echo "   → 'setup.sh' eliminado. 'init_investigation.sh' es el punto de entrada único."
else
    echo "   → 'setup.sh' no encontrado. Root ya estaba limpio en este punto."
fi

# ── 4. Asegurar .gitignore para evitar que la viruta vuelva ──────────────────
echo ""
echo "🛡️  [PASO 4] Reforzando .gitignore para blindar el root..."
GITIGNORE_ENTRIES=(
    "logs/runtime/"
    "*.pid"
    "*.log"
    "*_log.txt"
    "dash_logs.txt"
    ".env"
)
for entry in "${GITIGNORE_ENTRIES[@]}"; do
    if ! grep -qF "$entry" .gitignore 2>/dev/null; then
        run "echo '$entry' >> .gitignore"
        echo "   → Añadido a .gitignore: $entry"
    else
        echo "   → Ya ignorado: $entry"
    fi
done

echo ""
echo "✨ [HIGIENE BÉLICA] Root restaurado. El Búnker está listo para ser una Plantilla de GitHub."
echo ""
ls -1 --group-directories-first | grep -v '^\.git$'
