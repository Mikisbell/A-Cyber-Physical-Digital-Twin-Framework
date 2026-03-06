import openseespy.opensees as ops
import yaml
from pathlib import Path

# Carga de la SSOT (Solo lectura para simulación simple)
PARAMS_PATH = Path(__file__).parent.parent.parent / "config" / "params.yaml"

def load_sim_params():
    try:
        with open(PARAMS_PATH, 'r') as f:
            cfg = yaml.safe_load(f)
            
        return {
            "mass": cfg["structure"]["mass_m"]["value"],
            "k": cfg["structure"]["stiffness_k"]["value"],
            "fy": cfg["material"]["yield_strength_fy"]["value"],
            "xi": cfg["damping"]["ratio_xi"]["value"]
        }
    except Exception as e:
        raise RuntimeError(
            f"SSOT load failed: {e}. "
            f"Verify config/params.yaml exists and is valid YAML."
        ) from e

P = load_sim_params()

def init_model():
    """Inicializa un oscilador de 1 GDL simple en OpenSeesPy"""
    ops.wipe()
    ops.model('basic', '-ndm', 1, '-ndf', 1)
    
    # Nodos
    ops.node(1, 0.0)
    ops.node(2, 0.0)
    
    # Restricciones
    ops.fix(1, 1)
    
    # Material
    ops.uniaxialMaterial('Elastic', 1, P["k"])
    
    # Elemento cero-longitud
    ops.element('zeroLength', 1, 1, 2, '-mat', 1, '-dir', 1)
    
    # Masa
    ops.mass(2, P["mass"])
    
    # Análisis dinámico básico
    ops.timeSeries('Linear', 1)
    ops.pattern('Plain', 1, 1)
    # ops.load(2, 1.0) # Esto se hará desde bridge.py dinámicamente
    
    ops.system('BandGeneral')
    ops.numberer('Plain')
    ops.constraints('Plain')
    ops.integrator('Newmark', 0.5, 0.25)
    ops.algorithm('Newton')
    ops.analysis('Transient')
    
    print(f"[OPENSEES] 1-DOF model initialized (m={P['mass']}kg, k={P['k']}N/m)")
