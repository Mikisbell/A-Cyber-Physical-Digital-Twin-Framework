# Q1 Paper Roadmap: Unified Cryptographic Digital Twin with Neural Surrogate

## Target Journal
- **Primary**: Engineering Structures (Elsevier, Q1, IF ~5.5)
- **Alternative**: Structural Health Monitoring (SAGE, Q1, IF ~5.7)
- **Backup**: Automation in Construction (Elsevier, Q1, IF ~10.3)

## Proposed Title
"Cryptographic Digital Twin with Physics-Guided Neural Surrogate for Real-Time Seismic Assessment of Recycled Concrete Infrastructure"

## Novelty Statement
First framework that unifies:
1. Edge-computed physics-based data integrity (Guardian Angel + SHA-256)
2. Physics-Guided Neural Network surrogate (5000x NLTHA speedup)
3. C&DW material-specific damping corrections
4. Uncertainty-quantified remaining useful life (MC Dropout)

No existing SHM framework combines cryptographic data integrity with PgNN surrogates.

## Paper Structure (IMRaD Extended)

### 1. Introduction (~1500 words)
- SHM state of art [Farrar 2007, Sohn 2004, Flah 2021]
- C&DW challenge: heterogeneity, sustainability mandates [RILEM, Silva 2014]
- Gap: no framework combines data integrity + fast prediction + material specificity
- Contributions (4 bullets)

### 2. Theoretical Background (~2000 words)
- 2.1 SDOF/MDOF dynamics, Duhamel integral, Newmark integration
- 2.2 C&DW material properties (E, rho, k_term, xi_CDW)
- 2.3 PgNN architecture: 1D-CNN + Temporal Attention + FEM-guided loss
- 2.4 SHA-256 hash chaining for tamper evidence
- 2.5 MC Dropout for Bayesian uncertainty quantification

### 3. System Architecture (~1500 words)
- 3.1 SSOT governance (params.yaml -> params.h + params.py)
- 3.2 Edge hardware (Nicla Sense ME + LoRa + BHI260AP)
- 3.3 Guardian Angel filter (3 physics gates)
- 3.4 Engram cryptographic ledger
- 3.5 Closed-loop bridge (Kalman + jitter watchdog + Red Lines)

### 4. Numerical Framework (~2000 words)
- 4.1 OpenSeesPy SDOF model (C&DW parameters from SSOT)
- 4.2 OpenSeesPy MDOF model (N=3 and N=10 RC frames, Concrete02+Steel02)
- 4.3 PEER NGA-West2 ground motion database (289 records)
- 4.4 PgNN training: FEM-guided loss with actual f_int from fiber sections
- 4.5 Data augmentation and train/val/test split

### 5. Results (~3000 words)
- 5.1 Cross-validation A/B: Traditional vs Belico Stack (500 cycles)
- 5.2 Fragility analysis: Multi-PGA sweep (0.1-0.8g)
- 5.3 Sensitivity analysis (Saltelli indices)
- 5.4 Response spectrum: Pisco 2007, E.030 site amplification
- 5.5 C&DW damping advantage (Eurocode 8 correction, 10.6%)
- 5.6 PgNN surrogate: R^2=0.786 (N=3), R^2=0.713 (N=10)
- 5.7 Transfer learning: N=3 -> N=10 (98.2% accuracy retention)
- 5.8 Real-time inference: 2ms CPU latency (5000x speedup)
- 5.9 LSTM TTF with MC Dropout (when N>=30 Engram records)
- 5.10 Combined prediction: PgNN instant IDR + LSTM long-term TTF

### 6. Discussion (~1500 words)
- Data integrity under adversarial conditions
- PgNN vs full NLTHA: accuracy-latency tradeoff
- C&DW passive resilience quantification
- Limitations: synthetic data, SDOF simplifications, xi=7.5% assumption
- Comparison with existing SHM-DT frameworks

### 7. Conclusions (~500 words)
- 8 key findings
- Open-source availability
- Future work: field deployment, multi-structure monitoring

## Data Requirements
- [x] Synthetic cross-validation (cv_results.json) — DONE
- [x] Spectral analysis Pisco 2007 — DONE
- [x] PgNN model N=3 (R^2=0.786) — DONE (Hybrid-Twin repo)
- [x] PgNN model N=10 (R^2=0.713) — DONE (Hybrid-Twin repo)
- [ ] Field data (30+ min real sensor recording) — NEEDED for Q2, nice for Q1
- [ ] LSTM TTF with real Engram data (N>=30) — NEEDED

## Figure Plan (10-12 figures)
1. System architecture block diagram
2. Guardian Angel filter flowchart
3. A/B cross-validation bar chart
4. Fragility curve (PGA vs blocked payloads)
5. Sensitivity tornado chart (Saltelli)
6. Response spectrum Sa(T) — raw vs filtered vs site-amplified
7. C&DW vs virgin concrete damping comparison
8. PgNN architecture diagram (1D-CNN + Attention + FC)
9. PgNN predictions vs NLTHA ground truth (scatter + R^2)
10. Transfer learning: N=3 vs N=10 accuracy comparison
11. Real-time inference latency histogram
12. Combined prediction workflow: PgNN (instant) + LSTM (long-term)

## Reference Target: 50+ references
- [x] 42 in bibliography_engine.py — expand to 50+ with PgNN/surrogate refs

## Prerequisites Before Writing
1. Integrate PgNN surrogate into Belico Stack pipeline (DONE: pgnn_surrogate.py)
2. Run PgNN inference on Pisco 2007 record through Belico Stack
3. Generate combined figures (Belico + Hybrid-Twin data)
4. Expand bibliography with PgNN/surrogate/transfer learning refs

## Timeline Estimate
- Conference paper submitted -> Q3/Q4 data collection -> Q1 writing
- Q1 draft: after field data campaign and PgNN integration validation
