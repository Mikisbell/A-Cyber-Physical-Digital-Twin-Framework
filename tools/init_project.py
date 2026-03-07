#!/usr/bin/env python3
"""
tools/init_project.py — Project Bootstrapper
==============================================
Minimal setup: asks project name and domain, then generates
a PRD skeleton and empty params.yaml ready for AI-guided research.

Everything else (material selection, parameters, literature review)
happens during the Claude session — not here.

Usage:
  python3 tools/init_project.py              # New project setup
  python3 tools/init_project.py --reset      # Start fresh (backs up existing)
"""

import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
YAML_PATH = ROOT / "config" / "params.yaml"
PRD_PATH = ROOT / "PRD.md"
GENERATOR = ROOT / "tools" / "generate_params.py"


def ask(prompt: str, default=None) -> str:
    suffix = f" [{default}]" if default else ""
    while True:
        raw = input(f"  {prompt}{suffix}: ").strip()
        if not raw and default:
            return default
        if raw:
            return raw
        print("    (campo obligatorio)")


def ask_choice(prompt: str, options: list[dict]) -> dict:
    print(f"\n  {prompt}\n")
    for i, opt in enumerate(options, 1):
        print(f"    {i}. {opt['label']}")
        if opt.get("desc"):
            print(f"       {opt['desc']}")
    while True:
        raw = input(f"\n  Elige (1-{len(options)}): ").strip()
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(options):
                return options[idx]
        except ValueError:
            pass
        print(f"    (elige un numero del 1 al {len(options)})")


def banner(text: str):
    w = 55
    print(f"\n{'=' * w}")
    print(f"  {text}")
    print(f"{'=' * w}")


def info(text: str):
    print(f"  >> {text}")


# ─── Domain definitions ────────────────────────────────────────────────────

DOMAINS = [
    {
        "label": "structural — Analisis sismico / estructural",
        "key": "structural",
        "solver": "OpenSeesPy",
        "desc": "Columnas, porticos, muros, puentes. Sensor: acelerometro.",
        "research_hint": "Material (concreto, acero, madera), geometria, carga sismica",
    },
    {
        "label": "water — Fluidos / hidraulica",
        "key": "water",
        "solver": "FEniCSx (Navier-Stokes)",
        "desc": "Tuberias, canales, presas, flujo interno.",
        "research_hint": "Fluido (agua, aceite), geometria del dominio, condiciones de borde",
    },
    {
        "label": "air — Viento / aerodinamica",
        "key": "air",
        "solver": "FEniCSx / SU2",
        "desc": "Carga de viento en edificios, tuneles, puentes.",
        "research_hint": "Condicion atmosferica, geometria de obstaculo, velocidad de viento",
    },
]


# ─── Minimal params.yaml skeleton ──────────────────────────────────────────

def generate_skeleton(project_name: str, domain: dict) -> dict:
    """Generate a minimal params.yaml with nulls — to be filled during research."""
    return {
        "metadata": {
            "project": project_name,
            "version": "1.0.0",
            "last_updated": str(date.today()),
            "author": "",
            "config_hash": "",
        },
        "project": {"domain": domain["key"]},
        "material": {
            "name": "",
            "elastic_modulus_E": {"value": None, "units": "Pa", "symbol": "E"},
            "yield_strength_fy": {"value": None, "units": "Pa", "symbol": "fc"},
            "poisson_ratio": {"value": None, "units": "dimensionless", "symbol": "nu"},
            "density": {"value": None, "units": "kg/m^3", "symbol": "rho"},
            "thermal_conductivity": {"value": None, "units": "W/m*K", "symbol": "k_term"},
        },
        "structure": {
            "stiffness_k": {"value": None, "units": "N/m", "symbol": "k",
                            "firmware_var": "STIFFNESS_K", "simulation_var": "k"},
            "mass_m": {"value": None, "units": "kg", "symbol": "m",
                       "firmware_var": "MASS_M", "simulation_var": "mass"},
            "natural_frequency_fn": {"value": None, "units": "Hz",
                                     "symbol": "fn", "computed": True},
        },
        "damping": {
            "method": "rayleigh",
            "ratio_xi": {"value": None, "units": "dimensionless", "symbol": "xi",
                         "firmware_var": "DAMPING_RATIO", "simulation_var": "xi"},
        },
        "acquisition": {
            "sample_rate_hz": {"value": 100, "units": "Hz",
                               "firmware_var": "SAMPLE_RATE_HZ",
                               "simulation_var": "dt"},
            "sensor_pin": {"value": "A0", "firmware_var": "SENSOR_PIN"},
            "serial_baud": {"value": 115200, "firmware_var": "SERIAL_BAUD"},
        },
        "temporal": {
            "dt_simulation": {"value": 0.01, "units": "s"},
            "max_jitter_ms": {"value": 5, "units": "ms"},
            "buffer_depth": {"value": 10, "units": "packets"},
            "handshake_token": {"value": f"BELICO_SYNC_{date.today().year}"},
        },
        "signal_processing": {
            "kalman": {
                "enabled": True,
                "process_noise_q": {"value": 1e-5},
                "measurement_noise_r": {"value": 0.01},
            },
        },
        "guardrails": {
            "max_stress_ratio": {"value": 0.6},
            "convergence_tolerance": {"value": 1e-6},
            "max_sensor_outlier_sigma": {"value": 3.0},
        },
    }


# ─── PRD skeleton ───────────────────────────────────────────────────────────

def generate_prd(project_name: str, domain: dict, author: str) -> str:
    return f"""# PRD — {project_name}
# Version: 1.0.0 | Autor: {author} | Fecha: {date.today()}

---

## 1. Problema

<!-- Describe el problema de investigacion que quieres resolver -->
<!-- Ejemplo: "No existen datos de campo sobre el comportamiento sismico de..." -->

(Por definir durante la sesion de investigacion)

---

## 2. Vision

<!-- En una frase: que va a lograr este proyecto? -->

(Por definir)

---

## 3. Usuario

**{author}** — Investigador.
- Dominio: {domain['label']}
- Solver: {domain['solver']}

---

## 4. Alcance del Paper

<!-- Que tipo de paper vas a producir? -->

| Aspecto | Valor |
|---------|-------|
| Tipo | (Conference / Q4 / Q3 / Q2 / Q1) |
| Target journal | (Por definir) |
| Datos requeridos | (Sinteticos / Campo / Laboratorio) |
| Estructura | (Por definir durante EXPLORE) |

---

## 5. Parametros a Investigar

El agente AI te guiara para completar estos parametros durante la sesion:

- **Material**: {domain['research_hint']}
- **Config**: `config/params.yaml` (actualmente con valores null — se llenara con la investigacion)
- **Propagacion**: `python3 tools/generate_params.py`

---

## 6. Pipeline

```
config/params.yaml (SSOT)
    |
    v
src/firmware/params.h  +  src/physics/params.py
    |                          |
    v                          v
Sensor (campo)          Simulacion ({domain['solver']})
    |                          |
    v                          v
data/raw/               data/processed/
    |                          |
    +----------+---------------+
               |
               v
        articles/drafts/  -->  PDF
```

---

## 7. Siguiente Paso

Abre Claude Code en este directorio y di:

```
Engram conecto
```

El sistema cargara este PRD, identificara los parametros faltantes,
y te guiara para investigar y completar la configuracion.
"""


# ─── Main ──────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Belico Stack — Project Bootstrap")
    parser.add_argument("--reset", action="store_true",
                        help="Backup existing config and start fresh")
    args = parser.parse_args()

    banner("BELICO STACK — NUEVO PROYECTO")
    print("  Solo necesito 2 cosas. El resto lo investigamos juntos en Claude.")

    # Backup if needed
    if args.reset:
        for f in [YAML_PATH, PRD_PATH]:
            if f.exists():
                backup = f.with_suffix(f"{f.suffix}.bak.{date.today()}")
                shutil.copy2(f, backup)
                info(f"Backup: {backup.name}")

    # ── 1. Project name ──
    banner("NOMBRE DEL PROYECTO")
    project_name = ask("Como se llama tu proyecto?", "mi-proyecto")

    # ── 2. Domain ──
    banner("DOMINIO")
    domain = ask_choice("En que area trabajas?", DOMAINS)
    info(f"Dominio: {domain['key']} ({domain['solver']})")

    # ── 3. Author (optional) ──
    author = ask("Tu nombre (autor)", "")

    # ── Generate files ──
    banner("GENERANDO ARCHIVOS")

    # params.yaml skeleton (all nulls — to be filled during research)
    YAML_PATH.parent.mkdir(parents=True, exist_ok=True)
    cfg = generate_skeleton(project_name, domain)
    cfg["metadata"]["author"] = author

    class CustomDumper(yaml.SafeDumper):
        pass

    def float_representer(dumper, value):
        if value != value:
            return dumper.represent_scalar("tag:yaml.org,2002:float", ".nan")
        if abs(value) >= 1e6 or (0 < abs(value) < 1e-3):
            return dumper.represent_scalar(
                "tag:yaml.org,2002:float", f"{value:.6e}")
        return dumper.represent_scalar(
            "tag:yaml.org,2002:float", f"{value:g}")

    CustomDumper.add_representer(float, float_representer)

    with open(YAML_PATH, "w") as f:
        f.write(f"# SSOT — {project_name}\n")
        f.write(f"# Generado por init_project.py el {date.today()}\n")
        f.write("# Valores null = pendiente de investigacion\n")
        f.write("# Regenerar derivados: python3 tools/generate_params.py\n\n")
        yaml.dump(cfg, f, Dumper=CustomDumper, default_flow_style=False,
                  allow_unicode=True, sort_keys=False)
    info(f"config/params.yaml (esqueleto con nulls)")

    # PRD skeleton
    prd_content = generate_prd(project_name, domain, author)
    with open(PRD_PATH, "w") as f:
        f.write(prd_content)
    info(f"PRD.md (plantilla lista para investigar)")

    # Propagate (will work with nulls — generate_params handles them)
    if GENERATOR.exists():
        result = subprocess.run(
            [sys.executable, str(GENERATOR)],
            capture_output=True, text=True)
        if result.returncode == 0:
            info("params.h + params.py propagados")
        else:
            info("Propagacion pendiente (params.yaml tiene valores null)")

    # ── Done ──
    banner("LISTO")
    print(f"""
  Proyecto:  {project_name}
  Dominio:   {domain['key']} ({domain['solver']})
  PRD:       PRD.md
  Config:    config/params.yaml (valores pendientes de investigacion)

  SIGUIENTE PASO:
  Abre Claude Code en este directorio y di:

    Engram conecto

  Claude leera el PRD, identificara que parametros faltan,
  y te guiara para investigarlos y completar la configuracion.
  No necesitas saber los valores de antemano — eso es parte
  del proceso de investigacion.
""")


if __name__ == "__main__":
    main()
