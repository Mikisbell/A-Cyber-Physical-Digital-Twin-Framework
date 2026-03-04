# 🧠 Skill: Procesamiento de Señales Cognitivas (Shadow Play)

## Descripción
Esta skill capacita al Verifier y a los agentes de diseño para integrar filtros numéricos (como el Filtro de Kalman) en arquitecturas de Gemelos Digitales de tiempo real, distinguiendo anomalías sensóricas de fallos estructurales.

## Fundamento de Ingeniería Civil y Sistemas
Un pico de aceleración puede significar dos cosas:
1. **Ruido electromagnético (Anomalía Sensórica):** Altas frecuencias puras sin contenido energético que dañe la estructura. No se debe abortar.
2. **Impacto / Ruptura (Fallo Estructural):** Transmisión de energía real al sistema. El protocolo de aborto debe actuar.

Un Buffer Activo (Promedio Móvil) introduce **retraso de fase** (phase lag), lo que significa que OpenSeesPy recibe la señal retrasada. 
El **Filtro de Kalman** mitiga el retraso de la señal mientras penaliza la varianza (ruido) del instrumento de medición.

---

## Cómo usar el Filtro de Kalman en el Lazo Cerrado (bridge.py)

El filtro debe importarse de `simulation/kalman.py` e inicializarse con las matrices de varianza `Q` y `R` definidas en `config/params.yaml`.

```python
from simulation.kalman import RealTimeKalmanFilter1D

# Parámetros desde config/params.yaml
q = cfg["signal_processing"]["kalman"]["process_noise_q"]["value"]
r = cfg["signal_processing"]["kalman"]["measurement_noise_r"]["value"]

kf = RealTimeKalmanFilter1D(q=q, r=r)

# En el loop: reemplazar el buffer continuo por el filtro
accel_cruda = pkt["accel_g"]
accel_filtrada = kf.step(accel_cruda)
# Inyectar accel_filtrada en OpenSeesPy
```

## Guardrails del Verifier con Kalman

Si vas a auditar un experimento donde se activó el filtro de Kalman, debes incluir el PASO 7 en tu validación:
**PASO 7 — Varianza del Estimador:** `(accel_cruda - accel_filtrada)` debe ser una distribución normal de media cero. Si hay un sesgo (offset) persistente, el filtro está divergiendo o el acelerómetro de Arduino perdió calibración geométrica (Zero-G Offset shift).
