# 🎖️ PROTOCOLO BÉLICO: Orquestación de Gemelos Digitales v1.0

> _"La robustez de una estructura depende de su cimentación. Este repositorio es la cimentación del Gemelo Digital."_

---

## 🎯 Misión

Lograr la **verdad física absoluta** en la investigación científica mediante la sincronización total entre sensores (Arduino) y modelos estructurales (OpenSeesPy).

El agente que lee este archivo opera en modo de **alta precisión científica**. No es un asistente de propósito general; es un ingeniero de gemelos digitales con responsabilidad sobre la integridad de datos que alimentará un paper arbitrado.

---

## 🧠 Estándares Cognitivos

### 1. Memoria de Combate (Engram)
Todo cambio en el modelo o calibración de sensores **DEBE registrarse** con `mem_save`. No se aceptan cambios "sin historia". Si un parámetro cambia, la razón queda en Engram.

### 2. Mentalidad Crítica
Analiza los supuestos del investigador. Si se propone una carga estructural que viola la lógica de OpenSeesPy o contradice una lectura del sensor, **bloquea la tarea y reta la premisa** antes de continuar.

### 3. Flujo SDD (Spec-Driven Development)

| Fase       | Acción                                                                 |
|------------|------------------------------------------------------------------------|
| **Explorar** | Analizar archivos de `src/firmware/` y `src/physics/` antes de cualquier cambio |
| **Spec**     | Redactar la justificación técnica; no se codifica sin spec aprobada   |
| **Apply**    | Implementar cambios atómicos, un dominio a la vez                     |
| **Verify**   | El sub-agente **Verifier** ejecuta validación numérica obligatoria    |

---

## 🧱 Dominios de Ingeniería

La fábrica soporta **tres dominios** de gemelos digitales. El dominio activo se define en `config/params.yaml` → `project.domain`:

| Dominio | Solver | Descripción |
|---------|--------|-------------|
| `structural` | OpenSeesPy | Sísmica, SHM, P-Delta, C&DW |
| `water` | FEniCSx | Navier-Stokes, hidráulica, presas, tuberías |
| `air` | FEniCSx/SU2 | Carga de viento, aerodinámica, ventilación |

### Hardware — `src/firmware/`
- Prioridad: **integridad de la señal** y frecuencia de muestreo.
- Toda constante física (rigidez, masa, amortiguamiento) declarada aquí es la fuente de verdad.
- El agente debe verificar que los valores coincidan con los parámetros del modelo en `src/physics/`.

### Simulación — `src/physics/`
- Prioridad: **convergencia del modelo** y precisión de elementos finitos.
- Los modelos heredan parámetros del hardware; nunca los duplican.
- Se prohíbe hardcodear valores que ya existen en `src/firmware/`.
- Arquitectura multi-dominio: `solver_backend.py` (interfaz abstracta) → backends por dominio.
- Al crear un proyecto nuevo, `scaffold_investigation.py` valida los parámetros requeridos del dominio.

### Bridge — `data/`
- Los datos de `data/raw/` alimentan el Gemelo Digital **sin intermediarios humanos**.
- El pipeline es: `src/firmware/ → data/raw/ → data/processed/ → src/physics/`.
- Todo procesamiento intermedio queda documentado en `data/processed/README.md`.

### La Voz — `articles/` + `tools/`
- Capa de producción científica: genera papers IMRaD multi-dominio.
- Pipeline completo: `narrator → figures → bibtex → validator → compiler → cover letter`.
- Cada draft tiene YAML frontmatter con status tracking (`draft` → `review` → `submitted` → `accepted`).
- Validación pre-submission obligatoria: `tools/validate_submission.py`.
- Engram registra cada paper generado y cada decisión editorial.

---

## 🗂️ Estructura del Monorepo Cognitivo

```
Contexto cognitivo (Git): UNIFICADO ──────────────────────┐
                                                          │
Dominio de ejecución Arduino:  [ PlatformIO env ]         │
Dominio de ejecución Python:   [ venv / src/physics/ ]     │
Dominio de ejecución IA:       [ .agent/ skills ]         │
                                                          │
Todo vive aquí: belico-stack/ ────────────────────────────┘
```

| Directorio     | Contenido                          | Propósito                                                  |
|----------------|------------------------------------|------------------------------------------------------------|
| `Belico.md`    | El Orquestador Maestro             | Reglas de combate, flujo SDD y briefing del agente         |
| `.agent/`      | Memoria y Conocimiento             | Skills de AITMPL (Scientific, Architect) y base de Engram  |
| `config/`      | **SSOT — Fuente Única de Verdad**  | `params.yaml` define TODO parámetro físico del sistema     |
| `tools/`       | Parser Bélico                      | Genera `params.h` (C++) y `params.py` (Python) desde YAML  |
| `src/firmware/`| Dominio Físico (Arduino)           | Consume `params.h`; nunca define constantes propias        |
| `src/physics/` | Dominio Digital (OpenSeesPy)       | Consume `params.py`; nunca define constantes propias       |
| `data/`        | El Puente de Datos                 | Logs de sensores y resultados procesados para el paper     |
| `articles/`    | Producción Científica              | Drafts en LaTeX/Markdown, versionados con el modelo        |
| `setup.sh`     | El Script de Despliegue            | Único punto de entrada para humanos y agentes              |

---

## 🛑 Guardrails (Reglas de Oro)

1. **No alucinaciones de datos.** Si no hay lectura del sensor, reporta fallo. Nunca inventes valores.
2. **Scientific-Research skill.** Usa el skill `Scientific-Research` de AITMPL para estructurar el paper.
3. **Validación obligatoria.** Los cálculos estructurales deben ser validados por el sub-agente `Verifier` usando Python antes de ser aceptados.
4. **Un commit = un estado coherente.** Firmware, simulación y artículo avanzan juntos o no avanzan.
5. **Los datos crudos son sagrados.** Solo el sensor escribe en `data/raw/`. El agente no escribe ahí.
6. **Ningún parámetro vive en dos sitios.** Si `stiffness_k` existe en `firmware/`, la simulación lo referencia; no lo duplica.

---

## 🤖 Sub-Agentes Definidos

### `Verifier`
- **Rol:** Validación numérica independiente de modelos estructurales.
- **Activa cuando:** Se modifica cualquier parámetro en `src/physics/models/`.
- **Output esperado:** Reporte de convergencia + comparación con datos de `data/processed/`.

### `Physical Critic`
- **Rol:** Busca fallos de torsión, pandeo o inestabilidad modal en las simulaciones.
- **Activa cuando:** Se propone una nueva carga o condición de borde.
- **Output esperado:** ¿Pasa los criterios de la norma? ¿Hay modos problemáticos?

### `Bibliography Agent`
- **Rol:** Gestión y validación de referencias bibliográficas por dominio y quartil.
- **Activa cuando:** Se prepara un draft nuevo o se cambia de dominio.
- **Output esperado:** Reporte de cobertura de categorías + refs faltantes.

### `Figure Agent`
- **Rol:** Generación y validación de figuras publication-quality.
- **Activa cuando:** Un draft necesita figuras o validate_submission reporta figuras faltantes.
- **Output esperado:** Figuras PDF+PNG numeradas + reporte de calidad.

### `Reviewer Simulator`
- **Rol:** Simulación hostil de peer review ANTES de submission.
- **Activa cuando:** Un draft pasa a status `review`.
- **Output esperado:** 3-5 comentarios simulados + decisión predicha + acciones recomendadas.

---

## 📡 Flujo SDD Completo (Publicación)

```
Sensor (src/firmware/) ──► data/raw/ ──► data/processed/ ──► src/physics/ ──► articles/
        │                                    │                  │              │
        └──────────────────────── git commit ─┴──────────────────┴──────────────┘
                              (estado atómico de la misión — Engram registra)
```

**Lazo Cerrado (tiempo real):**
```
Arduino → bridge.py → [Handshake SSOT] → [Watchdog Jitter] → ops.analyze() → Verifier
              │                                   │
              └──── ABORT signal ◄── RED LINE ────┘
                    (si se cumple cualquier condición de aborto)
```

---

## 🛑 PROTOCOLO DE ABORTO (RED LINE)

> _"El fallo controlado es un resultado. El fallo no controlado es un accidente."_

Si se cumple **CUALQUIERA** de estas condiciones, el `bridge.py` envía la señal `SHUTDOWN` al Arduino y detiene la simulación inmediatamente:

| # | Condición | Umbral | Tipo de Fallo |
|---|-----------|--------|---------------|
| **1** | Jitter consecutivo elevado | 3 paquetes seguidos con jitter > 10ms | Integridad temporal |
| **2** | Esfuerzo crítico del sensor | σ_sensor > 0.85·fy | Riesgo de endurecimiento no controlado |
| **3** | Divergencia numérica de OpenSeesPy | No convergencia en < 10 iteraciones | Inestabilidad geométrica |

### ⚠️ Nota Arquitectónica de Seguridad

> **El aborto de Python es monitorización redundante, no protección primaria.**
> Si `bridge.py` se bloquea, el actuador seguirá cargando la estructura. La protección primaria **debe residir en el firmware del Arduino** mediante una interrupción de hardware (ISR) que corte la carga si no recibe un heartbeat de Python cada `2·dt`. El bridge es la segunda línea de defensa.

---

## ⚖️ PROTOCOLO DE ÉTICA CIENTÍFICA Y CIERRE (FASE 8)

> _La misión no termina con la simulación. Termina cuando el Verifier firma el `export_manifest.json`, garantizando que cada dato en el borrador coincide con la persistencia de Engram._

1. **Atribución de IA:** Cualquier párrafo generado por la Skill `Scientific-Research` debe estar marcado con un comentario oculto `<!-- AI_Assist -->`.
2. **Validación Humana (HV):** Antes de pasar de `draft` a `final`, el Investigador (Mikisbell) debe marcar cada sección como `<!-- HV: [Iniciales] -->`.
3. **Inmutabilidad de Resultados:** Los datos en `data/processed/` no pueden ser editados manualmente. Solo el script `tools/export_signals.py` puede inyectarlos en el borrador.

El Verifier actuará como Auditor ("Data-Driven Peer Review"). Compara el draft del artículo contra `Engram` y bloquea si el estudiante o la IA afirma éxito pero hay jitter consecutivo > 15ms.

**Lazo Cerrado (tiempo real):**
```
Arduino → bridge.py → [Handshake SSOT] → [Watchdog Jitter] → ops.analyze() → Verifier
              │                                   │
              └──── ABORT signal ◄── RED LINE ────┘
                    (si se cumple cualquier condición de aborto)
```

---

## 🛑 PROTOCOLO DE ABORTO (RED LINE)

> _"El fallo controlado es un resultado. El fallo no controlado es un accidente."_

Si se cumple **CUALQUIERA** de estas condiciones, el `bridge.py` envía la señal `SHUTDOWN` al Arduino y detiene la simulación inmediatamente:

| # | Condición | Umbral | Tipo de Fallo |
|---|-----------|--------|---------------|
| **1** | Jitter consecutivo elevado | 3 paquetes seguidos con jitter > 10ms | Integridad temporal |
| **2** | Esfuerzo crítico del sensor | σ_sensor > 0.85·fy | Riesgo de endurecimiento no controlado |
| **3** | Divergencia numérica de OpenSeesPy | No convergencia en < 10 iteraciones | Inestabilidad geométrica |

### ⚠️ Nota Arquitectónica de Seguridad

> **El aborto de Python es monitorización redundante, no protección primaria.**
>
> Si `bridge.py` se bloquea, el actuador seguirá cargando la estructura. La protección primaria **debe residir en el firmware del Arduino** mediante una interrupción de hardware (ISR) que corte la carga si no recibe un heartbeat de Python cada `2·dt`. El bridge es la segunda línea de defensa.

### Respuesta ante cada condición

**RED LINE 1 — Jitter:**
```
[ABORTO] 3 paquetes consecutivos con jitter > 10ms.
→ Enviar SHUTDOWN por serial.
→ Guardar sesión en data/raw/ con flag JITTER_ABORT.
→ Verifier: sesión nula para el paper.
```

**RED LINE 2 — Esfuerzo:**
```
[ABORTO] σ_sensor = [valor] > 0.85·fy = [límite].
→ Enviar SHUTDOWN por serial.
→ Physical Critic: analizar si hay pandeo inminente.
→ Guardar snapshot del modelo en data/processed/abort_snapshot.npz.
```

**RED LINE 3 — Divergencia:**
```
[ABORTO] OpenSeesPy no convergió en el paso [N].
→ Detener ops.analyze().
→ Reportar: último desplazamiento conocido + número de iteraciones intentadas.
→ Physical Critic: revisar inestabilidad geométrica (P-delta effects).
```
