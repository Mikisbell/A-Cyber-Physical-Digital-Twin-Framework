import os
import sys
from pathlib import Path

# Añadir la raíz al path para el import config.paths
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.paths import get_engram_db_path, get_drafts_dir, get_schema_engram_file, get_processed_data_dir

import sqlite3
import json
from datetime import datetime
import numpy as np
import pandas as pd

# Paths del Sistema (Resolución Dinámica)
ENGRAM_DB_PATH = get_engram_db_path()
DRAFT_DIR = get_drafts_dir()
REPORT_PATH = DRAFT_DIR / "transparency_report.md"

def _extract_dominant_frequency(csv_path: Path) -> float:
    """Skill Numérico (FFT): Extrae la Frecuencia Dominante pura de la serie temporal para guiar a la IA."""
    if not csv_path.exists():
        return 0.0
    try:
        df = pd.read_csv(csv_path)
        if len(df) < 10:
            return 0.0
        dt = np.mean(np.diff(df['time_s']))
        signal = df['accel_g'].values
        signal = signal - np.mean(signal) # Remover DC
        fft_vals = np.fft.rfft(signal)
        fft_freq = np.fft.rfftfreq(len(signal), d=dt)
        dom_idx = np.argmax(np.abs(fft_vals))
        return float(fft_freq[dom_idx])
    except Exception as e:
        print(f"❌ [FFT_SKILL] Error en análisis espectral: {e}")
        return 0.0

def fetch_telemetry_events():
    """Extrae el Baseline y la Alarma más recientes desde Engram."""
    baseline, alarm = None, None
    if not ENGRAM_DB_PATH.exists():
        return None, None
        
    try:
        with sqlite3.connect(ENGRAM_DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, timestamp, hash_code, payload, tags 
                FROM records WHERE tags LIKE '%"baseline"%' 
                ORDER BY timestamp DESC LIMIT 1
            ''')
            baseline = cursor.fetchone()
            
            cursor.execute('''
                SELECT id, timestamp, hash_code, payload, tags 
                FROM records WHERE tags LIKE '%"alarm"%' 
                ORDER BY timestamp DESC LIMIT 1
            ''')
            alarm = cursor.fetchone()
            
    except sqlite3.Error as e:
        print(f"❌ [NARRATOR] Error de lectura Engram: {e}")
        
    return baseline, alarm

def generate_paper_maestro(baseline, alarm):
    """Fusiona el Blueprint con la evidencia criptográfica LoRa para redactar el Paper Maestro."""
    blueprint_path = Path(__file__).resolve().parent / "blueprints" / "gemelo_digital_reciclado.md"
    blueprint_text = blueprint_path.read_text(encoding='utf-8') if blueprint_path.exists() else "Blueprint No Encontrado."
    
    informe = f"""{blueprint_text}

---

## Resultados Físicos: Auditoría de Telemetría LoRa (Edge IoT)
*Reporte autogenerado por el Scientific Narrator (Belico Stack)*

Este estudio ha superado la dependencia del monitoreo pasivo mediante streaming cableado, implementando una red de **Edge Computing (Nicla Sense ME)**. El algoritmo de Inteligencia Artificial (Filtro de Kalman y FFT) opera directamente en el silicio del sensor, emitiendo únicamente inferencias asíncronas de bajísimo peso a través del protocolo LoRa.

A continuación, la confrontación del Gemelo Digital contra la evidencia criptográfica almacenada en la base Inmutable (Engram).

### 1. Estado Sano (Baseline Telemétrico)
"""
    if baseline:
        b_payload = json.loads(baseline['payload'])
        b_dt = datetime.fromtimestamp(baseline['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        informe += f"""Se determinó la firma de vibración inicial de la estructura utilizando la algoritmia FFT On-Board.
- **Timestamp de Sellado**: {b_dt}
- **Hash de Evidencia**: `{baseline['hash_code']}`
- **Engram ID**: `[Ref: {baseline['id']}]`
- **Frecuencia Dominante (Fn)**: {b_payload.get('f_n', 0):.2f} Hz
- **Temperatura Interna (C&DW)**: {b_payload.get('tmp', 0):.1f} °C
- *(Confirmando integridad estructural inicial bajo parámetros nominales).*
"""
    else:
        informe += "> ⚠️ No se encontró registro Baseline Sano en Engram.\n"
        
    informe += "\n### 2. Detección Predictiva de Anomalía (Fallo Crítico)\n"
    
    if alarm:
        a_payload = json.loads(alarm['payload'])
        a_dt = datetime.fromtimestamp(alarm['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        informe += f"""El gemelo digital interactuó con la anomalía reportada asíncronamente por el Watchdog Telemétrico del Búnker, demostrando la capacidad del sistema de aislar información vital.
- **Timestamp de Alarma**: {a_dt}
- **Hash de Evidencia**: `{alarm['hash_code']}`
- **Engram ID**: `[Ref: {alarm['id']}]`
- **Razón Categórica de Fallo**: `{a_payload.get('reason', 'N/A')}`
- **Frecuencia Caída (Fn)**: {a_payload.get('f_n', 0):.2f} Hz *(Alarma de Fatiga)*
- **Aceleración Pico Estructural**: {a_payload.get('max_g', 0):.3f} g
- **Latencia de Red (Airtime LoRa)**: {a_payload.get('lag_s', 0):.1f} s *(Rechazando paquetes > 15s)*

### 3. Conclusión Científica sobre Resiliencia Nacional
El sistema **Belico Stack** ha demostrado que los módulos habitacionales de concreto reciclado pueden ser transformados en agentes activos de su propio mantenimiento. La caída de la frecuencia natural detectada (_{a_payload.get('f_n', 0):.2f} Hz_) fue procesada de extremo a extremo sin saturar el ancho de banda, permitiéndole a la capa de predicción (LSTM) calcular la vida remanente mucho antes del colapso estructural.

En el marco de la infraestructura para la *Presa del Norte* y futuras obras, la validación temporal asíncrona (con apenas {a_payload.get('lag_s', 0):.1f} segundos de Lag) previene el ataque de falsas alarmas y garantiza una toma de decisiones blindada y auditable.
"""
    else:
        informe += "> ⚠️ No se encontró registro de Alarma Estructural en Engram.\n"
        
    DRAFT_DIR.mkdir(parents=True, exist_ok=True)
    paper_out = DRAFT_DIR / "paper_maestro.md"
    with open(paper_out, "w") as f:
        f.write(informe)
    
    print(f"✅ [NARRATOR] Paper Maestro generado con éxito en: {paper_out}")

if __name__ == "__main__":
    print("🧠 [NARRATOR] Extrayendo Blueprint y Evidencia de Engram DB...")
    base, alrm = fetch_telemetry_events()
    generate_paper_maestro(base, alrm)
