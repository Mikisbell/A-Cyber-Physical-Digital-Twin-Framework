// AUTO-GENERATED — No editar manualmente.
// Fuente: config/params.yaml  |  Hash: f376d4ba704b123b
// Regenerar: python3 tools/generate_params.py
#pragma once

#define CONFIG_HASH     "f376d4ba704b123b"

// ── Material ──
#define MATERIAL_NAME   "Concreto Liviano Reciclado C&DW"
#define E_MODULUS       20e9
#define YIELD_STRENGTH  20e6
#define RHO             1800.0
#define K_TERM          0.51

// ── Structure ──
#define STIFFNESS_K     5000.0
#define MASS_M          1000.0

// ── Damping ──
#define DAMPING_RATIO   0.05

// ── Acquisition ──
#define SERIAL_BAUD     115200
#define SAMPLE_RATE_HZ  100

// ── Kalman Filter ──
#define KF_Q            1e-05
#define KF_R            0.01

// ── Temporal Sync ──
#define HANDSHAKE_TOKEN "BELICO_SYNC_2026"
#define MAX_JITTER_MS   5

// ── Guardrails ──
#define MAX_STRESS_RATIO  0.6
#define MAX_SENSOR_SIGMA  3.0
