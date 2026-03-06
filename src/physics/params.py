# AUTO-GENERATED — No editar manualmente.
# Fuente: config/params.yaml  |  Hash: f376d4ba704b123b
# Regenerar: python3 tools/generate_params.py

CONFIG_HASH = "f376d4ba704b123b46716b5ae31de1e08fa7b5cc63fca77daec73cf0435037cd"

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
