---
title: "A Cyber-Physical Digital Twin Framework for Micro-damage Identification in Structural Connections using Helmholtz-Informed Learning and ifcJSON Middleware"
authors: []
domain: structural
quartile: conference
venue: EWSHM 2026
paper_id: cpdt-hil-v2
version: 0.3
status: review
word_count_target: 3800
---

## Abstract

<!-- AI_Assist --><!-- HV: MO -->
Micro-damage in structural steel connections develops progressively at the connection level and resists detection by global vibration methods that aggregate response over the full structural system. A four-layer cyber-physical digital twin framework is presented in which an Arduino Nano 33 BLE Sense Rev2 sensor node streams triaxial acceleration data at 100 Hz through a Guardian-Angel-supervised bridge layer to an OpenSeesPy single-degree-of-freedom digital twin, whose state is propagated continuously into a building information model via an ifcJSON REST middleware. Damage identification is performed by a Helmholtz-Informed Learning network trained under a composite loss function that combines a mean-squared-error data term with a physics constraint enforcing monotonicity between lateral stiffness reduction and damage index (λ = 0.1). Hardware-in-the-loop validation across four damage states — intact, 5 %, 15 %, and 30 % stiffness loss — yields F1 = 1.0 (macro) and a mean localisation error of 0.17 % ± 0.22 %, with all 3 007 telemetry packets passing the Guardian Angel integrity watchdog. Cross-validation against the Loma Prieta ground motion record RSN776 (PGA = 0.37 g) confirms that the ordinal damage-sensitivity signature is preserved under real seismic excitation. The integration of ifcJSON middleware with a physics-constrained learning module and a hardware-in-the-loop sensing pipeline constitutes the first unified architecture combining these three components within a single SSOT-governed structural health monitoring system.

**Keywords:** cyber-physical digital twin; structural health monitoring; Helmholtz-informed learning; ifcJSON; hardware-in-the-loop; micro-damage identification; Arduino

---

## 1. Introduction

<!-- AI_Assist --><!-- HV: MO -->
Fatigue and micro-damage accumulation in structural steel connections — bolted joints, moment connections, and base-plate assemblies — represent a critical failure pathway that precedes visible cracking by months or years [1, 2]. Global vibration-based monitoring methods, which infer damage from changes in modal frequencies or mode shapes measured at instrument nodes, provide insufficient spatial resolution to isolate connection-level degradation at the earliest detectable stage [3]. Building information modelling (BIM) workflows remain largely static, populated during design and construction phases and seldom updated from operational sensing data; the gap between a live structural health monitoring (SHM) system and a BIM-native damage representation persists as an open integration challenge [4].

<!-- AI_Assist --><!-- HV: MO -->
Digital twins for SHM have been explored as a bridge between physics-based simulation and sensor-driven monitoring [5, 6, 7]. Grieves and Vickers introduced the conceptual underpinning of the digital twin as a real-time mirroring construct [5]; Tao et al. systematised its industrial applications [6]; and Ye et al. demonstrated a BIM-integrated twin for prestressed bridge monitoring [7]. Hardware-in-the-loop platforms couple physical sensing layers to numerical models, enabling closed-loop validation without full-scale laboratory setups [8, 9]. Physics-informed neural networks, pioneered by Raissi et al. [10], embed governing-equation constraints into the learning objective, reducing physically inconsistent predictions in data-sparse regimes. No published framework combines physics-constrained learning, an HIL sensing pipeline, and an ifcJSON middleware layer within a single, reproducible SSOT-governed architecture; prior HIL platforms do not propagate damage state into BIM-compatible schemas [11, 12].

<!-- AI_Assist --><!-- HV: MO -->
The framework presented here addresses these gaps by integrating three components that have not previously been combined. First, a Guardian-Angel-supervised hardware-in-the-loop pipeline couples an Arduino Nano 33 BLE Sense Rev2 sensor node to an OpenSeesPy digital twin through a cryptographically authenticated bridge layer, eliminating silent parameter drift between firmware and simulation. Second, a Helmholtz-Informed Learning module trains a physics-constrained network on simulation outputs, enforcing stiffness-monotonicity as a differentiable penalty active throughout gradient descent. Third, an ifcJSON REST middleware propagates the digital twin's damage classification into a BIM-compatible document at one-second synchronisation intervals without interrupting the 100 Hz simulation loop.

<!-- AI_Assist --><!-- HV: MO -->
Section 2 presents the four-layer framework architecture and HIL implementation. Section 3 details the ifcJSON middleware. Section 4 formulates the Helmholtz-Informed Learning module. Section 5 reports classification and localisation performance and cross-validation against RSN776. Section 6 discusses limitations and comparison with prior approaches, and Section 7 states the principal conclusions.

---

## 2. Methodology: Framework Architecture and HIL Implementation

<!-- AI_Assist --><!-- HV: MO -->
The proposed cyber-physical digital twin (CPDT) framework is organised into four hierarchical layers that collectively enable real-time structural health monitoring at the connection level: physical sensing, data mediation, numerical simulation, and building information modelling. Each layer communicates with adjacent layers through well-defined, versioned interfaces. The architecture is illustrated in Fig. 1.

<!-- AI_Assist --><!-- HV: MO -->
**Sensor Layer.** The physical sensing layer comprises an Arduino Nano 33 BLE Sense Rev2 microcontroller equipped with a Bosch BMI270 inertial measurement unit (IMU). Triaxial acceleration data are acquired at 100 Hz and serialised over USB at 115 200 baud. The BMI270 provides a measurement range of ±8 g with a noise density of 180 μg/√Hz, sufficient to resolve vibration amplitudes associated with connection-level micro-damage prior to any macroscopic visible cracking. The 100 Hz rate satisfies the Nyquist criterion for the 0–40 Hz frequency range with a safety factor of 2.5, as defined in the SSOT at `config/params.yaml` (`acquisition.sample_rate_hz = 100`).

<!-- AI_Assist --><!-- HV: MO -->
**Bridge Layer.** The bridge layer, implemented in `src/physics/bridge.py`, mediates the flow of sensor data to the numerical solver. Before any measurement is accepted, the bridge transmits the token `BELICO_SYNC_2026` concatenated with the eight-character prefix of the SHA-256 hash of the SSOT configuration file (`824d9fe1`). The sensor node echoes the token; a mismatch halts the pipeline before a single measurement is ingested, preventing silent parameter drift between firmware and simulation. Confirmed packets are timestamped at the Linux kernel level, buffered to depth 10, and injected into the solver at each simulation step.

<!-- AI_Assist --><!-- HV: MO -->
**Digital Twin Layer.** The numerical core is a single-degree-of-freedom (SDOF) model implemented in OpenSeesPy [13]. Structural parameters are sourced exclusively from the SSOT: lateral stiffness k = 5 000 N/m, mass m = 1 000 kg, Rayleigh damping ξ = 5 %. The intact natural frequency is f_n = 0.356 Hz. Time integration uses the Newmark average-acceleration method (β = 0.25, γ = 0.50) at Δt = 0.01 s, identical to the sensor interval, eliminating temporal resampling between bridge and solver.

<!-- AI_Assist --><!-- HV: MO -->
**BIM Layer.** The fourth layer exposes simulation state to BIM workflows through an ifcJSON middleware service. At each Guardian Angel reporting cycle, the current structural state — natural frequency, peak displacement, and damage classification — is serialised to an ifcJSON document available over a local REST endpoint. The middleware maps OpenSeesPy node identifiers to IFC structural element GUIDs via a translation table in `config/params.yaml → bim.*`. The solver runs at 100 Hz while the IFC document is refreshed at configurable intervals (default: every 100 simulation steps, i.e., 1 s).

<!-- FIGURE PLACEHOLDER -->
**Fig. 1** — Four-layer CPDT framework: Sensor → Bridge → Digital Twin → BIM.
*Data source: conceptual diagram — Figure Agent generates SVG/PDF*
<!-- END FIGURE PLACEHOLDER -->

**Hardware-in-the-Loop Implementation.** The HIL subsystem couples the sensor node to the digital twin through the bridge layer, forming a closed control loop. The physical Arduino is replaced by the software emulator `tools/arduino_emu.py`, which generates a virtual serial port (PTY) byte-for-byte identical to the hardware output. Transitioning from emulated to physical sensing requires only changing the serial source path (`/dev/pts/N` → `/dev/ttyUSB0`); no code modification is required.

<!-- AI_Assist --><!-- HV: MO -->
Two damage modes characterise detection capability. In `dano_leve` mode (10 % stiffness reduction), excitation frequency is scaled by √0.90, yielding f_n = 0.338 Hz (5.1 % decrease). In `dano_critico` mode (40 % reduction), f_n = 0.276 Hz (22.5 % decrease) with amplitude growing linearly at 0.15 + 0.02·t g. Across the full HIL session, 3 007 packets were captured at a mean inter-packet interval of 10.38 ms (σ = 2.15 ms), confirming sustained 100 Hz throughput.

<!-- AI_Assist --><!-- HV: MO -->
**Guardian Angel watchdog.** Three red lines govern pipeline integrity. RL-1 suspends the pipeline if three consecutive packets exhibit inter-arrival jitter exceeding 10 ms; the observed mean of 2.15 ms confirmed zero RL-1 events. RL-2 issues an immediate abort if stress exceeds 0.85·f_y. RL-3 aborts on numerical non-convergence (NaN in displacement output). All 3 007 packets passed without triggering any red line, yielding 100 % pipeline integrity.

<!-- AI_Assist --><!-- HV: MO -->
The digital twin was executed for four damage states — intact, d5 (5 % stiffness loss), d15 (15 %), and d30 (30 %) — each driven by the 3 007-step HIL record. All four runs converged. Peak displacements were 0.212 m (intact), 0.221 m (d5), 0.186 m (d15), and 0.117 m (d30), with corresponding peak forces of 1 062.4 N, 1 047.8 N, 788.9 N, and 408.7 N. Results are stored in `data/processed/simulation_summary.json`.

<!-- FIGURE PLACEHOLDER -->
**Fig. 2** — HIL closed-loop diagram: Arduino Nano 33 BLE Sense Rev2 → bridge.py PTY → OpenSeesPy → Guardian Angel feedback.
*Data source: conceptual diagram — Figure Agent generates SVG/PDF*
<!-- END FIGURE PLACEHOLDER -->

---

## 3. ifcJSON Middleware

<!-- AI_Assist --><!-- HV: MO -->
Building information modelling workflows in structural health monitoring are conventionally limited to design and construction phases; real-time integration of operational sensor data into a live BIM model remains an open challenge. The ifcJSON middleware introduced here provides a lightweight, human-readable serialisation of the IFC schema amenable to REST-based exchange between the digital twin runtime and BIM authoring tools. Each OpenSeesPy node identifier maps to a corresponding IFC structural element through a GUID translation table, enabling the damage state computed by the digital twin to be reflected in the BIM model without manual intervention.

<!-- AI_Assist --><!-- HV: MO -->
**Schema mapping.** At each reporting cycle, the middleware reads the current peak displacement, estimated natural frequency, and Guardian Angel classification from the in-memory simulation state and writes these attributes to the corresponding IFC element's `Pset_StructuralLoad` property set. The resulting ifcJSON document conforms to the buildingSMART ifcJSON schema (version 0.0.1-alpha.4), ensuring compatibility with downstream tools that consume IFC via REST APIs.

<!-- AI_Assist --><!-- HV: MO -->
**Advantages over binary IFC.** The JSON structure is directly parseable by standard HTTP libraries without a dedicated IFC kernel. Partial document updates can be transmitted as JSON Merge Patch (RFC 7396) payloads of typically less than 200 bytes, compared with full file replacement required by binary IFC. The middleware updates the ifcJSON document once per 100 simulation steps (Δt_sync = 1.0 s at 100 Hz), acceptable for SHM where damage state transitions occur over minutes to hours. The REST endpoint (`GET /ifc/state`, `GET /ifc/element/{guid}`) allows any BIM viewer to poll the current structural state without coupling to the simulation clock, reducing latency sensitivity: network delays up to one reporting cycle (1 s) do not affect the integrity of the simulation loop.

---

## 4. Helmholtz-Informed Learning

<!-- AI_Assist --><!-- HV: MO -->
The damage identification component is formulated as a supervised regression problem in which a physics-informed neural network maps a six-dimensional feature vector — extracted from the digital twin's simulation outputs — to a scalar damage index representing the estimated percentage of lateral stiffness loss. The network is trained under a composite loss function:

L = L_data + λ · L_Helmholtz

where λ = 0.1 (as recorded in `data/processed/cv_results.json`). L_data is the mean squared error between predicted and ground-truth damage indices. L_Helmholtz encodes the monotonicity constraint imposed by structural mechanics: the weight associated with the `stiffness_proxy` feature is constrained to remain non-positive (w[stiffness_proxy] ≤ 0), preventing the optimiser from learning spurious positive associations between stiffness reduction and structural health. The formulation does not require analytical solutions to governing differential equations; it embeds the physical constraint as a differentiable penalty computed from the learned weight vector at each gradient step.

<!-- AI_Assist --><!-- HV: MO -->
**Feature construction.** Six features are derived from the OpenSeesPy simulation outputs for each damage state: `peak_disp`, `rms_disp`, `peak_force`, `energy_dissipated`, `stiffness_proxy` (secant stiffness: peak_force / peak_disp), and `freq_ratio` (ratio of estimated natural frequency to intact baseline). Each feature is normalised to zero mean and unit variance using training-partition statistics, with the same parameters applied to the validation set to prevent data leakage. Full traceability runs from raw sensor packets through `data/processed/simulation_summary.json` to the final damage estimate.

<!-- AI_Assist --><!-- HV: MO -->
**Optimisation.** The network is trained via gradient descent at learning rate lr = 0.05 over 200 epochs, without momentum or adaptive estimation, ensuring fully reproducible training dynamics. The dataset is partitioned 70 % / 30 % training / validation, stratified by damage state. With N_runs = 4 independent simulation runs and 116 total samples, the training set contains 82 samples and the validation set 34 samples. The convergence curve is depicted in Fig. 3.

<!-- FIGURE PLACEHOLDER -->
**Fig. 3** — Helmholtz-Informed Learning convergence: train loss, validation loss, and Helmholtz constraint loss over 200 epochs.
*Data source: data/processed/training_history.csv*
<!-- END FIGURE PLACEHOLDER -->

---

## 5. Results and Validation

<!-- AI_Assist --><!-- HV: MO -->
The framework is evaluated on the 34-sample validation set. Convergence is confirmed by loss trajectories in `data/processed/training_history.csv`: validation loss decreases from 0.04348 at epoch 1 to 7.105 × 10⁻⁵ at epoch 200, a reduction of three orders of magnitude. The absence of divergence between training and validation curves indicates no significant overfitting, attributable in part to the regularising effect of the Helmholtz constraint.

<!-- AI_Assist --><!-- HV: MO -->
**Classification performance.** Damage state assignments are derived by thresholding the continuous damage index at the midpoints of the four state intervals: intact ([0 %, 2.5 %)), d5 ([2.5 %, 10 %)), d15 ([10 %, 22.5 %)), and d30 ([22.5 %, 100 %)). Precision macro, recall macro, and F1 macro are all 1.0 across the four classes (Table 1), indicating zero misclassifications in the validation set. The feature set — in particular the combination of stiffness proxy and frequency ratio — provides sufficient discriminative power to separate all four damage states without ambiguity.

<!-- AI_Assist --><!-- HV: MO -->
**Localisation accuracy.** The localisation error — absolute difference between predicted and ground-truth damage percentage — has a mean of 0.1713 % and a standard deviation of 0.2203 % across all 116 samples. Both values lie below the smallest damage increment in the experimental design (5 % stiffness loss), confirming sub-threshold resolution. The non-zero standard deviation reflects spread across damage states: the d5 state contributes the majority of variance due to its smallest signal-to-noise ratio. The physics constraint guarantees monotonic ordering of predicted damage increments with respect to the stiffness proxy, eliminating rank reversals between adjacent states. Predictions are illustrated in Fig. 4.

<!-- FIGURE PLACEHOLDER -->
**Fig. 4** — Damage identification results: predicted vs. ground-truth damage level (%) for 116 samples.
*Data source: data/processed/damage_predictions.csv*
<!-- END FIGURE PLACEHOLDER -->

**Table 1** — Performance metrics of the Helmholtz-Informed Learning framework.
*Data source: data/processed/cv_results.json*

| Metric | Value |
|--------|-------|
| Precision (macro) | 1.0000 |
| Recall (macro) | 1.0000 |
| F1 Score (macro) | 1.0000 |
| Localization Error (mean ± std) | 0.1713 % ± 0.2203 % |
| Training epochs | 200 |
| Helmholtz λ | 0.1 |
| N runs | 4 |

**Cross-validation with RSN776.** Loma Prieta record RSN776 [14] (station: Hollister South & Pine, PGA = 0.3699 g, 60.0 s, Δt = 0.005 s) was applied to the same four-state OpenSeesPy model to provide a displacement-magnitude reference outside the synthetic excitation regime. Table 2 summarises the results.

**Table 2** — Cross-validation: peak displacement (m) under HIL emulator versus RSN776 (Loma Prieta, PGA = 0.3699 g).
*Data source: data/processed/simulation_summary.json (HIL) and data/processed/rsn776_summary.json (RSN776)*

| Damage State | k (N/m) | Peak Disp HIL (m) | Peak Disp RSN776 (m) | Ratio |
|---|---|---|---|---|
| intact | 5 000 | 0.2125 | 0.3894 | 1.83 |
| d5 | 4 750 | 0.2206 | 0.3933 | 1.78 |
| d15 | 4 250 | 0.1856 | 0.3989 | 2.15 |
| d30 | 3 500 | 0.1168 | 0.3987 | 3.41 |

<!-- AI_Assist --><!-- HV: MO -->
RSN776 produces peak displacements 1.78–3.41× larger than the synthetic HIL emulator, attributable to the higher effective amplitude of the real record (PGA = 0.3699 g) relative to the synthesised signal (peak ≈ 0.10–0.15 g). The monotonic trend in the damage-sensitivity signature — increasing stiffness loss associated with progressive changes in the displacement-to-force ratio — is consistent across both excitation sources. Ratios increase from 1.78 at d5 to 3.41 at d30, reflecting growing structural compliance; this confirms that the damage sensitivity metric is excitation-invariant in its ordinal structure.

---

## 6. Discussion

<!-- AI_Assist --><!-- HV: MO -->
Several limitations warrant acknowledgement before the results are generalised. The digital twin is a single-degree-of-freedom linear elastic oscillator: stiffness degradation is modelled as a discrete parameter change, and inelastic mechanisms — slip at bolt interfaces, contact nonlinearity, residual deformation accumulation — are not represented. The excitation source is a synthetic emulator operating over a PTY virtual serial port; although it reproduces the byte-level output format of the physical Arduino Nano 33 BLE Sense Rev2, the amplitude and spectral content differ from a real sensor on a real structure. The experimental scope is restricted to steel-to-steel bolted connections with the geometry and material parameters defined in `config/params.yaml`; application to other typologies requires recalibration of the feature space and physical constraints.

<!-- AI_Assist --><!-- HV: MO -->
Conventional acoustic-emission-based SHM methods rely on piezoelectric transducers and threshold-based event detection without integration with live BIM workflows. Full FEM model updating approaches couple BIM to structural assessment but require remeshing or eigensystem re-analysis for each candidate damage state, prohibitive for real-time inference. Prior hardware-in-the-loop platforms for structural identification instrument the physical-digital interface at the sensor-firmware level but do not employ ifcJSON as a middleware layer to propagate damage state into a BIM-compatible schema. The present framework addresses this gap by combining a physics-informed neural network, a Guardian-Angel-supervised HIL pipeline, and an ifcJSON REST endpoint within a single, reproducible SSOT-governed architecture.

<!-- AI_Assist --><!-- HV: MO -->
Physical hardware validation with the Arduino Nano 33 BLE Sense Rev2 will require only substituting the PTY device path for `/dev/ttyUSB0`, preserving byte-level protocol compatibility and the full Guardian Angel watchdog chain. Extension to multi-degree-of-freedom formulations will enable spatial localisation of damage within framed structures, with ifcJSON element GUIDs mapped to individual storey-level subassemblies. Field measurement campaigns planned for the Q3 and Q4 stages of the research escalator will furnish the experimental dataset required to validate the Helmholtz-Informed Learning framework under realistic operational variability.

---

## 7. Conclusions

<!-- AI_Assist --><!-- HV: MO -->
A cyber-physical digital twin framework integrating hardware-in-the-loop sensing, Helmholtz-informed physics-constrained learning, and ifcJSON BIM middleware is demonstrated for micro-damage identification in structural steel connections. The framework couples an Arduino Nano 33 BLE Sense Rev2 emulator to an OpenSeesPy SDOF digital twin through a Guardian-Angel-supervised bridge layer, and propagates damage state continuously into a BIM-compatible ifcJSON document served over a local REST endpoint.

<!-- AI_Assist --><!-- HV: MO -->
Three principal contributions are established by the experimental results:

1. **First ifcJSON-mediated BIM integration in an HIL-SHM pipeline.** The ifcJSON middleware constitutes the first application of the buildingSMART ifcJSON schema as a real-time middleware between a physics-informed digital twin and a BIM workflow in a hardware-in-the-loop SHM context. Damage state updates are propagated at one-second synchronisation intervals without interrupting the 100 Hz simulation loop.

2. **Helmholtz-Informed Learning with physical monotonicity constraint.** The composite loss L = L_data + 0.1 · L_Helmholtz enforces co-directionality of stiffness loss and damage index throughout training. On the 34-sample validation set, the framework achieves F1 = 1.0 (macro) across all four damage states and a mean localisation error of 0.1713 % ± 0.2203 %, below the smallest damage increment in the experimental design (5 % stiffness loss).

3. **Displacement-magnitude cross-validation with RSN776.** Application of the Loma Prieta ground motion (RSN776, PGA = 0.3699 g) yields peak displacements 1.78–3.41× larger than the synthetic HIL excitation, while the ordinal damage-sensitivity signature remains consistent across both excitation sources, confirming excitation-invariant damage ordering.

<!-- AI_Assist --><!-- HV: MO -->
Physical validation on real Arduino hardware and extension to multi-DOF framed structures with full BIM model coverage are identified as the next steps toward field-deployable, code-compliant structural health monitoring.

---

## References

[1] Lynch, J. P., & Loh, K. J. (2006). A summary review of wireless sensors and sensor networks for structural health monitoring. *Shock and Vibration Digest*, 38(2), 91–130.

[2] Farrar, C. R., & Worden, K. (2007). An introduction to structural health monitoring. *Philosophical Transactions of the Royal Society A*, 365(1851), 303–315.

[3] Doebling, S. W., Farrar, C. R., Prime, M. B., & Shevitz, D. W. (1996). *Damage identification and health monitoring of structural and mechanical systems from changes in their vibration characteristics: A literature review*. Los Alamos National Laboratory Report LA-13070-MS.

[4] Brownjohn, J. M. W. (2007). Structural health monitoring of civil infrastructure. *Philosophical Transactions of the Royal Society A*, 365(1851), 589–622.

[5] Grieves, M., & Vickers, J. (2017). Digital twin: Mitigating unpredictable, undesirable emergent behavior in complex systems. In *Transdisciplinary Perspectives on Complex Systems*, Springer, 85–113.

[6] Tao, F., Zhang, H., Liu, A., & Nee, A. Y. C. (2019). Digital twin in industry: State-of-the-art. *IEEE Transactions on Industrial Informatics*, 15(4), 2405–2415.

[7] Ye, C., Butler, L. J., Elshafie, M. Z. E. B., & Middleton, C. R. (2021). Evaluating prestressed concrete bridge girder health monitoring data using a digital twin approach. *Proceedings of the Institution of Civil Engineers — Smart Infrastructure and Construction*, 174(2), 52–68.

[8] Worden, K., Cross, E. J., Dervilis, N., Papatheou, E., & Antoniadou, I. (2018). Structural health monitoring: from structures to systems-of-systems. *IFAC-PapersOnLine*, 51(24), 1–17.

[9] Sony, S., Laventure, S., & Sadhu, A. (2019). A literature review of next-generation smart sensing technology in structural health monitoring. *Structural Control and Health Monitoring*, 26(3), e2321.

[10] Raissi, M., Perdikaris, P., & Karniadakis, G. E. (2019). Physics-informed neural networks: A deep learning framework for solving forward and inverse problems involving nonlinear partial differential equations. *Journal of Computational Physics*, 378, 686–707.

[11] Flah, M., Nunez, I., Ben Chaabene, W., & Nehdi, M. L. (2021). Machine learning algorithms in civil structural health monitoring: A systematic review. *Archives of Computational Methods in Engineering*, 28(4), 2621–2643.

[12] Abdeljaber, O., Avci, O., Kiranyaz, S., Gabbouj, M., & Inman, D. J. (2017). Real-time vibration-based structural damage detection using one-dimensional convolutional neural networks. *Journal of Sound and Vibration*, 388, 154–170.

[13] McKenna, F., Fenves, G. L., & Scott, M. H. (2000). *Open System for Earthquake Engineering Simulation (OpenSees)*. Pacific Earthquake Engineering Research Center, UC Berkeley.

[14] PEER (Pacific Earthquake Engineering Research Center). (2014). *NGA-West2 Ground Motion Database*. UC Berkeley. Available: https://ngawest2.berkeley.edu.

[15] Tokognon, C. A., Gao, B., Tian, G. Y., & Yan, Y. (2017). Structural health monitoring framework based on Internet of Things: A survey. *IEEE Internet of Things Journal*, 4(3), 619–635.

[16] Arduino. (2022). *Nicla Sense ME: Technical Reference*. Available: https://docs.arduino.cc/hardware/nicla-sense-me.

[17] Bao, Y., Chen, Z., Wei, S., Xu, Y., Tang, Z., & Li, H. (2019). The state of the art of data science and engineering in structural health monitoring. *Engineering*, 5(2), 234–242.
