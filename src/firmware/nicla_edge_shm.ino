/*
 * src/firmware/nicla_edge_shm.ino
 * ============================================================================
 * Firmware BÉLICO EDGE AI para Arduino Nicla Sense ME
 * 
 * Actúa como un nodo IoT de procesamiento pesado en el borde.
 * En lugar de enviar aceleración en bruto a 100Hz (lo cual saturaría LoRa),
 * este microcontrolador maestrea internamente a 100Hz, limpia la señal con  
 * un Filtro de Kalman 1D, y acumula "ventanas" de 256 muestras (2.56 segs).
 * 
 * Luego ejecuta una Transformada Rápida de Fourier (FFT) On-Board
 * y emite UN SOLO PAQUETE con los resultados finales (Frecuencia Dominante, 
 * Aceleración Peak y Estado) hacia el módulo LoRa UART.
 * 
 * Dependencias de Librería Opcionales a instalar en Arduino IDE:
 *  - Arduino_BHY2 (Para sensores BHI260AP del Nicla Sense ME)
 *  - arduinoFFT (v1.x o v2.x)
 * ============================================================================
 */

#include "Arduino.h"
#include "Arduino_BHY2.h"
#include "params.h"  // SSOT — auto-generated from config/params.yaml
// #include "arduinoFFT.h" // Descomentar en IDE tras instalar arduinoFFT

// ─────────────────────────────────────────────────────────
// CONFIGURACION DE SHM Y FISICA (derivada de SSOT)
// ─────────────────────────────────────────────────────────
#define SAMPLES          WINDOW_SIZE_SAMPLES  // Potencia de 2 para FFT (SSOT)
#define SAMPLING_FREQ    ((float)SAMPLE_RATE_HZ)

// Umbrales de Seguridad (desde SSOT params.h)
#define NOMINAL_FN       NOMINAL_FN_HZ
#define FN_DROP_WARN     FN_DROP_WARN_RATIO
#define FN_DROP_CRIT     FN_DROP_CRIT_RATIO
#define MAX_G_CRIT       MAX_G_ALARM

// ─────────────────────────────────────────────────────────
// FILTRO DE KALMAN 1D P-DELTA (Edge AI)
// ─────────────────────────────────────────────────────────
class KalmanFilter1D {
private:
    float _q; // Process noise covariance
    float _r; // Measurement noise covariance
    float _p; // Estimation error covariance
    float _x; // State estimate

public:
    KalmanFilter1D(float q, float r, float p, float initial_value) {
        _q = q;
        _r = r;
        _p = p;
        _x = initial_value;
    }

    float step(float measurement) {
        // Predicción
        _p = _p + _q;
        
        // Actualización (Kalman Gain)
        float k = _p / (_p + _r);
        _x = _x + k * (measurement - _x);
        
        // Innovación (z - x) implícita en la ganancia
        _p = (1.0f - k) * _p;
        
        return _x;
    }
};

// Instancia del filtro (Q y R from SSOT params.h)
KalmanFilter1D kf(KF_Q, KF_R, 1.0, 0.0);

// ─────────────────────────────────────────────────────────
// MEMORIA Y FFT
// ─────────────────────────────────────────────────────────
SensorXYZ accel(SENSOR_ID_ACC);
Sensor temp(SENSOR_ID_TEMP);
Sensor hum(SENSOR_ID_HUM);

double vReal[SAMPLES];
double vImag[SAMPLES];
// arduinoFFT FFT = arduinoFFT(vReal, vImag, SAMPLES, SAMPLING_FREQ);

unsigned int sampleIndex = 0;
unsigned long sampling_period_us;
unsigned long microseconds;
float max_g_window = 0.0;

// Reloj Unix simulado (A ser ajustado por downlink si hay gateway)
unsigned long current_unix_epoch = 1710000000; 

// ─────────────────────────────────────────────────────────
// SETUP
// ─────────────────────────────────────────────────────────
void setup() {
    Serial.begin(SERIAL_BAUD);   // Consola Debug (USB, SSOT)
    Serial1.begin(LORA_BAUD); // Telemetría LoRa (SSOT)

    while (!Serial && millis() < 3000); // Espera opcional a la consola serial
    
    Serial.println("=========================================");
    Serial.println("[NICLA EDGE AI] Iniciando Motor BHI260AP...");
    
    // Inicializar el Fuser Core del Nicla
    BHY2.begin();
    accel.begin(SAMPLING_FREQ, 0); // 100Hz
    temp.begin();
    hum.begin();

    sampling_period_us = round(1000000.0 / SAMPLING_FREQ);
    
    Serial.println("[NICLA EDGE AI] Sensores Activos.");
    Serial.println("[NICLA EDGE AI] Capturando vectores base...");
    Serial.println("=========================================");
}

// ─────────────────────────────────────────────────────────
// LOOP PRINCIPAL
// ─────────────────────────────────────────────────────────
void loop() {
    // 1. Muestreo de estricto tiempo real
    microseconds = micros();
    
    // Actualiza datos de los sensores desde el BHI260AP Fuser Core
    BHY2.update();

    // 2. Extraer, Filtrar y Almacenar
    // Nicla reporta en "g" multiplicados por 4096 o un vector directo.
    // Usamos el vector X como eje fuerte.
    float raw_g = accel.x() / 4096.0; // Normalización típica BHI
    
    // Someter la lectura cruda a la purga de Kalman
    float clean_g = kf.step(raw_g);

    // Detección de peak (para la amplitud máxima de la ventana)
    if (abs(clean_g) > max_g_window) {
        max_g_window = abs(clean_g);
    }

    // Guardar para el análisis espectral
    vReal[sampleIndex] = clean_g;
    vImag[sampleIndex] = 0.0;
    
    sampleIndex++;

    // 3. Cuando la ventana está llena, ejecutar Edge AI
    if (sampleIndex >= SAMPLES) {
        /*
        // EJECUCIÓN DE LA FFT EN SILICIO (Descomentar con la librería)
        FFT.Windowing(FFT_WIN_TYP_HANN, FFT_FORWARD);
        FFT.Compute(FFT_FORWARD);
        FFT.ComplexToMagnitude();
        double peak_freq = FFT.MajorPeak();
        */
        
        // FFT not linked — skip structural alarm logic, report NO_FFT status
        double peak_freq = -1.0;  // Sentinel: no real measurement available
        
        // Lógica de Estado Estructural
        String stat;
        if (peak_freq < 0) {
            // FFT not available — report data only, no alarm logic
            stat = "NO_FFT";
        } else if (peak_freq < (NOMINAL_FN * FN_DROP_CRIT) || max_g_window > MAX_G_CRIT) {
            stat = "ALARM_RL2";
        } else if (peak_freq < (NOMINAL_FN * FN_DROP_WARN)) {
            stat = "WARN";
        } else {
            stat = "OK";
        }

        // Simulación de reloj RTC (Sumamos 2.56 segs por ventana)
        current_unix_epoch += (SAMPLES / SAMPLING_FREQ);

        // 4. Empaquetar el "Resumen Ejecutivo" para el canal angosto de LoRa
        // Formato esperado por el Watchdog Telemétrico del bridge.py
        float t_val = temp.value();
        float h_val = hum.value();
        
        char payload[128];
        snprintf(payload, sizeof(payload), 
          "LORA:T:%lu,TMP:%.1f,HUM:%.1f,FN:%.2f,MAX_G:%.3f,STAT:%s\n",
          current_unix_epoch, t_val, h_val, peak_freq, max_g_window, stat.c_str()
        );

        // 5. Emitir al Espacio (Transmisor Tx Serial1 hacia módulo LoRa)
        Serial1.print(payload);
        
        // Debug local en Base
        Serial.print("[EDGE EVENT] ");
        Serial.print(payload);

        // Reset de la ventana
        sampleIndex = 0;
        max_g_window = 0.0;
    }

    // Spin-lock para mantener los 100 Hz precisos
    while(micros() < (microseconds + sampling_period_us)) {
        // Yield para evitar freezing
    }
}
