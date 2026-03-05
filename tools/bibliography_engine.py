"""
tools/bibliography_engine.py — Motor de Citas Dinámicas para el EIU
===================================================================
Este módulo inyecta de forma autónoma las referencias académicas en el 
artículo Markdown final, basándose en los comandos y bases de datos 
utilizadas durante la campaña de Research Director.
"""

from pathlib import Path

# Base de datos maestra de referencias (Cofre del Conocimiento Q1)
CITATION_VAULT = {
    # ── Ingeniería Sísmica Local y Global ──
    "peer_berkeley": (
        "PEER (Pacific Earthquake Engineering Research Center), "
        "'NGA-West2 Ground Motion Database', UC Berkeley, 2014. "
        "Available: https://ngawest2.berkeley.edu."
    ),
    "cismid_peru": (
        "CISMID (Centro Peruano Japonés de Investigaciones Sísmicas), "
        "'Red Acelerográfica Nacional del Perú (REDACIS)', UNI, Lima, Perú. "
        "Available: http://www.cismid.uni.edu.pe."
    ),
    
    # ── Redes, Hardware y Sostenibilidad ──
    "belico_stack": (
        "Belico Stack Architecture, "
        "'Cryptographic Edge-AI Structural Health Monitoring via LoRa IoT', "
        "GitHub Open Source Initiative, 2026."
    ),
    "rilem_cdw": (
        "RILEM TC 235-CTC (2018). "
        "'Recommendations for the formulation, manufacturing and modeling of recycled aggregate concrete'. "
        "Materials and Structures, 51(5), 1-13."
    ),
    "shm_wsn": (
        "Lynch, J. P., & Loh, K. J. (2006). "
        "'A summary review of wireless sensors and sensor networks for structural health monitoring'. "
        "Shock and Vibration Digest, 38(2), 91-130."
    ),
    
    # ── Deep Learning (LSTM, PINNs, XAI) ──
    "lstm_ttf": (
        "Hochreiter, S., & Schmidhuber, J. (1997). "
        "'Long short-term memory'. Neural computation, 9(8), 1735-1780."
    ),
    "pinns_sota": (
        "Raissi, M., Perdikaris, P., & Karniadakis, G. E. (2019). "
        "'Physics-informed neural networks: A deep learning framework'. "
        "Journal of Computational physics, 378, 686-707."
    ),
    "xai_trust": (
        "Samek, W., Montavon, G., et al. (2019). "
        "'Explainable AI: interpreting, explaining and visualizing deep learning'. "
        "Springer Nature."
    )
}

def generate_bibliography(sources_used: list) -> str:
    """
    Construye la sección de referencias final del Markdown
    según las bases metodológicas consumidas.
    """
    bib_text = "\n## References\n"
    
    # Fuentes base innegociables para el marco teórico (C&DW, PINNs, LSTM, SHM)
    default_sources = ["belico_stack", "lstm_ttf", "pinns_sota", "xai_trust", "rilem_cdw", "shm_wsn"]
    
    # Combinar reduciendo duplicados
    all_sources = list(set(default_sources + sources_used))
    
    for idx, source_key in enumerate(all_sources, 1):
        if source_key in CITATION_VAULT:
            bib_text += f"[{idx}] {CITATION_VAULT[source_key]}\n"
        else:
            bib_text += f"[{idx}] Unknown Citation Key: {source_key}\n"
            
    return bib_text

if __name__ == "__main__":
    test_bib = generate_bibliography(["peer_berkeley"])
    print(test_bib)
