# AUTO-GENERATED — No editar manualmente.
# Fuente: config/params.yaml  |  Hash: 71bd0061bbcf0625
# Regenerar: python3 tools/generate_params.py

CONFIG_HASH = "71bd0061bbcf06255c6eaa83bf95edbe27e6b5eda44938713babd73e0889140d"

# Material
MATERIAL_NAME = "Concreto Liviano Reciclado C&DW"
E         = 20e9
fc        = 20e6
nu        = 0.2
rho       = 1800.0
k_term    = 0.51

# Estructura
k         = 5000.0

# Adquisición
BAUD_RATE = 115200
SAMPLE_RATE_HZ = 100

# Kalman
KF_ENABLED = True
KF_Q       = 1e-05
KF_R       = 0.01

# Temporal
DT         = 0.01
MAX_JITTER = 5
BUFFER_DEPTH = 10

# Nonlinear model status
NONLINEAR_READY = False
