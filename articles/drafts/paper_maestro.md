# 📜 Metodología de Detección de Micro-Daños en Conexiones Estructurales  
### mediante Hardware de Bajo Costo y Gemelo Digital Auditable

**Autor:** Mateo Mikkelsen (Ing. Civil / Ing. de Sistemas)  
**Repositorio:** `belico-stack` — Ecosistema de Investigación Estructural  
**Estado:** Fase de Calibración Completada · Validación de Campo: Pendiente

---

## Abstract

Se propone una metodología de **bajo costo y alta trazabilidad** para la detección temprana de micro-daños en conexiones estructurales (acero/concreto). El sistema integra un sensor de aceleración basado en Arduino (≈$20 USD), un Gemelo Digital no-lineal en OpenSeesPy (modelo P-Delta), un Filtro de Kalman en tiempo real para estimación de estado, y el motor narrativo AITMPL para traducción de evidencia técnica en informes auditables públicamente.

Toda anomalía detectada queda inmutable en una base de datos criptográfica (Engram), garantizando la transparencia requerida ante auditorías técnicas, académicas y ciudadanas.

> **Alcance actual:** La presente versión documenta la metodología completa y la validación del algoritmo de detección espectral (FFT) en entorno sintético. La validación de campo con hardware físico en estructuras reales se incorporará en la Sección 5 una vez completados los ensayos.

---

## 1. Marco Teórico

### 1.1 Variación de Frecuencia Natural como Indicador de Daño

La frecuencia natural de un sistema estructural de un grado de libertad es:

$$f_n = \frac{1}{2\pi}\sqrt{\frac{k}{m}}$$

Donde $k$ es la rigidez transversal de la conexión y $m$ es la masa tributaria. Bajo degradación por fatiga o micro-fisuras, $k$ decrece mientras $m$ permanece constante. Consecuencia directa: **$f_n$ cae de forma monotónica ante daño acumulado**, mucho antes de que el daño sea visible.

### 1.2 Efectos No Lineales (P-Delta)

Para conexiones esbeltas o estructuras con carga axial significativa, la rigidez efectiva incluye el término geométrico de segundo orden:

$$k_{ef} = k - \frac{P}{L}$$

El Gemelo Digital en OpenSeesPy incorpora este efecto mediante la formulación `geomTransf PDelta`, activando el Protocolo de Aborto (Red Line 2) cuando el esfuerzo supera $\sigma > 0.85 f_y$.

### 1.3 Filtro de Kalman como Separador de Ruido

El Filtro de Kalman estima el estado del sistema $\hat{x}_{k|k}$ minimizando el error cuadrático medio:

$$K_k = P_{k|k-1} H^T \left( H P_{k|k-1} H^T + R \right)^{-1}$$

La **Innovación** $z_k - H\hat{x}_{k|k-1}$ es la métrica central del SHM: si diverge sistemáticamente, la estructura ha cambiado su comportamiento dinámico respecto al modelo ideal.

---

## 2. Instrumentación y Protocolo SHM

| Componente | Tecnología | Función |
|---|---|---|
| Sensor | Arduino + MPU-6050 o MEMS | Adquisición de aceleración (≤100 Hz) |
| Canal | Puerto Serial / USB | Enlace Emulador→Bridge |
| Gemelo Digital | OpenSeesPy (Modelo P-Delta) | Predicción de comportamiento ideal |
| Estimador | Filtro de Kalman (1D) | Separar ruido eléctrico de respuesta estructural |
| Memoria | SQLite + SHA-256 (Engram) | Registro inmutable de anomalías |
| Narrador | Scientific Narrator + FFT Skill | Traducción de evidencia para uso cívico |

### 2.1 Protocolo de Aborto (Red Lines)

| Red Line | Condición | Acción |
|---|---|---|
| RL-1 | Jitter > 10ms en 3 paquetes consecutivos | SHUTDOWN por ruido de canal |
| RL-2 | σ_sensor > 0.85·fy | SHUTDOWN por esfuerzo crítico |
| RL-3 | OpenSeesPy no converge en < 10 iteraciones | SHUTDOWN por inestabilidad numérica |

---

## 3. Resultados de Calibración (Entorno Sintético)

**Protocolo de Certificación Metrológica V1** — `tools/synthetic_fft_audit.py`  
Condiciones: Señal armónica pura + 10% ruido Gaussiano · T=10s · fs=100Hz

| f_inyectada | f_detectada | Error (%) | Estado |
|---|---|---|---|
| 2.0 Hz | 2.00 Hz | 0.0% | PASS ✅ |
| 5.2 Hz | 5.20 Hz | 0.0% | PASS ✅ |
| 8.0 Hz | 8.00 Hz | 0.0% | PASS ✅ |
| 12.0 Hz | 12.00 Hz | 0.0% | PASS ✅ |
| 18.0 Hz | 18.00 Hz | 0.0% | PASS ✅ |

**Error Promedio: 0.00% · σ: 0.00% · 5/5 APROBADOS**

**Nota metodológica:** La validación en entorno PTY virtual está limitada a ventanas de ~0.6s (Δf = 1.67 Hz). El barrido sintético desacopla el algoritmo del canal de comunicación, validando el instrumento de medición de forma independiente. Con hardware Arduino real a 100 Hz continuo, la resolución espectral es Δf = 0.10 Hz (T=10s).

---

## 4. Inmutabilidad y Trazabilidad (Protocolo Engram)

Cada evento de aborto es firmado con SHA-256 y registrado en `engram.db`:

- **Hash de Verificación:** `c1d4aa4675ca0b1c2d0bcc1af05a90f02df524d8e902a3b375950bba15d2d2c9`
- **Evento de referencia:** `[Ref: Engram_ID_3]` — RL-2 ESFUERZO: σ=213.19MPa > 212.50MPa (5.2 Hz, Cámara de Tortura)
- **Verificación pública:** El hash puede ser confrontado contra el historial de Git en cualquier momento.

> El `dashboard` de Auditoría Ciudadana (`http://[host]:8080`) expone estos datos en modo Solo-Lectura para cualquier ciudadano con acceso a la red.

---

## 5. Validación de Campo — *[Pendiente]*

### 5.1 Caso de Aplicación: Proyecto Presa del Norte

*Esta sección se completará con los resultados de los ensayos físicos.*

- **Objetivo:** Validar la metodología en una estructura real con historia de servicio conocida.
- **Protocolo:** Instalar sensor en la zona de máximo cortante. Comparar $f_n$ medida vs. $f_n$ teórica de OpenSeesPy con la geometría as-built.
- **Criterio de daño:** Reducción de $f_n$ > 5% respecto al baseline indica degradación de rigidez no natural.

### 5.2 Caso de Aplicación: Infraestructura Comunitaria "LA ESPERANZA"

*Esta sección se completará con los resultados de los ensayos físicos.*

- **Objetivo:** Democratizar el diagnóstico estructural: un sensor de $20 USD puede sustituir una inspección de $5,000 USD en la primera línea de detección.
- **Protocolo de presentación ciudadana:** El Scientific Narrator traducirá los resultados al idioma del ciudadano no-técnico, certificando la independencia del juicio mediante la firma del Engram.

---

## Referencias Técnicas

- OpenSeesPy: McKenna, F. et al. *Open System for Earthquake Engineering Simulation* (OpenSEES) v3.5.8
- Kalman, R.E. (1960). *A New Approach to Linear Filtering and Prediction Problems.* J. Basic Engineering.
- Chopra, A.K. *Dynamics of Structures.* (Teoría de P-Delta y Análisis Modal)
- Stack Bélico v1.0: `belico-stack/README.md` — Certificación Metrológica V1 (2026-03-05)
