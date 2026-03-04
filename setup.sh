#!/bin/bash
# setup.sh — Inicializador del Ecosistema Bélico
# Plataforma objetivo: Linux (Ubuntu/Debian)
# Uso: ./setup.sh

set -e

echo "🚀 Iniciando despliegue de infraestructura profesional..."
echo "   Sistema operativo: $(uname -s) $(uname -m)"
echo ""

# ─────────────────────────────────────────
# 1. ESTRUCTURA DE CARPETAS
# ─────────────────────────────────────────
echo "📁 Verificando estructura de directorios..."
mkdir -p firmware/src simulation/models data/raw data/processed articles/drafts .agent/skills .agent/prompts
echo "   ✅ Directorios listos."

# ─────────────────────────────────────────
# 2. ENTORNO PYTHON — OpenSeesPy + Análisis
# ─────────────────────────────────────────
echo ""
echo "🔬 Configurando entorno Python para OpenSeesPy..."

cd simulation
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "   ✅ Entorno virtual creado en simulation/venv"
fi
source venv/bin/activate
pip install --upgrade pip --quiet
pip install openseespy numpy pandas matplotlib scipy --quiet
deactivate
cd ..

echo "   ✅ Dependencias de simulación instaladas."

# ─────────────────────────────────────────
# 3. PLATFORMIO — Dominio Arduino
# ─────────────────────────────────────────
echo ""
echo "⚡ Verificando PlatformIO (dominio hardware)..."

if ! command -v pio &> /dev/null; then
    echo "   PlatformIO no encontrado. Instalando via pip..."
    pip3 install --user platformio --quiet
    echo "   ✅ PlatformIO instalado."
else
    echo "   ✅ PlatformIO ya disponible: $(pio --version)"
fi

# ─────────────────────────────────────────
# 4. PERMISOS HARDWARE — Puerto Serial Arduino
# ─────────────────────────────────────────
echo ""
echo "🔌 Configurando acceso al puerto serial (Arduino)..."

# Añadir usuario al grupo dialout (necesario para /dev/ttyUSB* y /dev/ttyACM*)
CURR_USER=$(whoami)
if id -nG "$CURR_USER" | grep -qw "dialout"; then
    echo "   ✅ Usuario '$CURR_USER' ya está en el grupo dialout."
else
    echo "   Añadiendo '$CURR_USER' al grupo dialout..."
    sudo usermod -aG dialout "$CURR_USER"
    echo "   ✅ Listo. IMPORTANTE: debes cerrar sesión y volver a entrar para que surta efecto."
fi

# Regla udev para chips CH340/CH341 (Arduino UNO clones) y ATmega16U2 (Arduino UNO original)
UDEV_RULE_FILE="/etc/udev/rules.d/99-arduino.rules"
if [ ! -f "$UDEV_RULE_FILE" ]; then
    echo "   Creando regla udev para Arduino..."
    sudo tee "$UDEV_RULE_FILE" > /dev/null << 'EOF'
# Arduino UNO (ATmega16U2) y clones (CH340/CH341)
SUBSYSTEM=="tty", ATTRS{idVendor}=="2341", ATTRS{idProduct}=="0043", MODE="0666", GROUP="dialout"
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", MODE="0666", GROUP="dialout"
EOF
    sudo udevadm control --reload-rules && sudo udevadm trigger
    echo "   ✅ Regla udev instalada. Reconecta el Arduino si ya estaba conectado."
else
    echo "   ✅ Regla udev ya existe: $UDEV_RULE_FILE"
fi

# ─────────────────────────────────────────
# 5. COMPATIBILIDAD CLAUDE CODE / GEMINI
# ─────────────────────────────────────────
echo ""
echo "🔗 Creando enlace de compatibilidad..."

if [ ! -L "CLAUDE.md" ]; then
    ln -sf Belico.md CLAUDE.md
    echo "   ✅ Enlace CLAUDE.md → Belico.md creado."
else
    echo "   ✅ Enlace CLAUDE.md ya existe."
fi

# ─────────────────────────────────────────
# 6. GIT — Verificación
# ─────────────────────────────────────────
echo ""
echo "📦 Verificando control de versiones..."
if [ ! -d ".git" ]; then
    git init
    echo "   ✅ Repositorio Git inicializado."
else
    echo "   ✅ Repositorio Git ya existe."
fi

# ─────────────────────────────────────────
# RESUMEN
# ─────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎖️  STACK BÉLICO LISTO."
echo ""
echo "   Orquestador:   Belico.md (→ CLAUDE.md)"
echo "   Simulación:    simulation/venv"
echo "   Hardware:      firmware/ + platformio.ini"
echo "   Puerto serial: /dev/ttyUSB0 | /dev/ttyACM0"
echo "   Datos:         data/raw  →  data/processed"
echo "   Sub-agentes:   .agent/prompts/verifier.md"
echo "                  .agent/prompts/physical_critic.md"
echo ""
echo "   ⚠️  Si agregaste el usuario a dialout hoy,"
echo "   cierra sesión y vuelve a entrar para activar"
echo "   los permisos del puerto serial."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
