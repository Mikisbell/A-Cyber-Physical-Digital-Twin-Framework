# 🔧 Parser Bélico — Protocolo de Generación de Parámetros

## Propósito

Este directorio contiene las herramientas que **leen `config/params.yaml`** (la SSOT) y generan los archivos de parámetros para cada dominio de ejecución.

**Regla:** Nunca edites `firmware/src/params.h` ni `simulation/models/params.py` directamente. Siempre trabaja en `config/params.yaml` y regenera.

---

## Flujo de Generación

```
config/params.yaml   (SSOT — única fuente de verdad)
         │
         ├──► tools/generate_params.py
         │           │
         │           ├──► firmware/src/params.h      (C++ para Arduino)
         │           └──► simulation/models/params.py (Python para OpenSeesPy)
         │
         └──► config_hash.sha256   (hash del YAML — validado por Verifier)
```

---

## Archivos Generados

### `firmware/src/params.h`
Header de C++ con `#define` para cada parámetro. Arduino lo incluye con `#include "params.h"`.

Ejemplo de output esperado:
```c
// AUTO-GENERATED — NO EDITAR DIRECTAMENTE
// Fuente: config/params.yaml | Hash: [sha256]
#define STIFFNESS_K    5000.0f   // N/m
#define MASS_M         1000.0f   // kg
#define DAMPING_RATIO  0.05f     // dimensionless
#define SAMPLE_RATE_HZ 100       // Hz
#define SENSOR_PIN     A0
#define SERIAL_BAUD    115200
```

### `simulation/models/params.py`
Módulo Python con un diccionario de parámetros. OpenSeesPy lo importa con `from params import P`.

Ejemplo de output esperado:
```python
# AUTO-GENERATED — NO EDITAR DIRECTAMENTE
# Fuente: config/params.yaml | Hash: [sha256]
CONFIG_HASH = "[sha256]"
P = {
    "E":    200e9,    # Pa
    "fy":   250e6,    # Pa
    "k":    5000.0,   # N/m
    "mass": 1000.0,   # kg
    "xi":   0.05,     # dimensionless
    "dt":   0.01,     # s (1/sample_rate_hz)
}
GUARDRAILS = {
    "max_stress_ratio":        0.6,
    "convergence_tolerance":   1e-6,
    "max_slenderness":         120,
    "eccentricity_ratio":      0.10,
    "mass_participation_min":  0.90,
    "max_sensor_outlier_sigma": 3.0,
}
```

---

## Cómo Usar

```bash
# Desde la raíz del repo
python tools/generate_params.py

# El script reporta:
# ✅ firmware/src/params.h generado
# ✅ simulation/models/params.py generado
# ✅ config_hash.sha256 actualizado: [hash]
```

---

## Validación del Verifier (PASO 4-bis: Hash de Configuración)

El sub-agente Verifier compara el hash del `params.yaml` en el momento de la simulación contra el hash embebido en `params.py`. Si no coinciden:

> ❌ **ERROR DE FUENTE DE VERDAD — CONFIGURACIÓN DESINCRONIZADA**
> El firmware y la simulación están usando parámetros de versiones distintas.
> Acción: Ejecutar `python tools/generate_params.py` y repetir la simulación.
