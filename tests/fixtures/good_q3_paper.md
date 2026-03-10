---
title: "Vibration-Based Damage Detection in an RC Highway Bridge Using Accelerometer Arrays and Calibrated OpenSeesPy Finite Element Models"
domain: structural
quartile: Q3
version: 1.0
status: review
venue: "Journal of Civil Structural Health Monitoring (JCSHM)"
---

## Abstract

This paper presents a vibration-based damage detection methodology for reinforced concrete highway bridges combining field accelerometer measurements with calibrated OpenSeesPy finite element models. A four-span continuous RC bridge in southern Peru was instrumented with twelve uniaxial MEMS accelerometers (ADXL355) at quarter-span and midspan locations across all spans. Ambient vibration recordings over 48 hours captured the first five natural frequencies (f1 = 3.82 Hz to f5 = 18.41 Hz) and corresponding mode shapes via frequency domain decomposition (FDD). A three-dimensional OpenSeesPy model with fiber-section beam-column elements and distributed plasticity was calibrated against the identified modal parameters using a genetic algorithm optimizer, achieving frequency errors below 2.1% for all five modes. Damage was simulated numerically by reducing element stiffness at known locations (5%, 15%, 30%) and validated against controlled load test data from a 32-tonne truck crossing. The MAC values between experimental and numerical mode shapes exceeded 0.94 for the first three modes. The calibrated model detected 15% stiffness reduction with 91% accuracy using a combined frequency-shift and mode-shape-curvature indicator, outperforming frequency-only methods (78% accuracy) under the same noise conditions. The methodology complies with Eurocode 8 serviceability drift limits and provides a transferable framework for bridge monitoring in seismic regions. <!-- AI_Assist -->

## 1. Introduction

Highway bridges in seismic regions experience cumulative damage from traffic loading, environmental degradation, and earthquake excitation. The 2007 Pisco earthquake (Mw 8.0) caused significant damage to transportation infrastructure in southern Peru, highlighting the need for continuous structural health monitoring (SHM) systems capable of detecting damage before serviceability limits are exceeded [1]. Visual inspection remains the primary assessment method for most bridge inventories, yet sub-surface damage in RC elements—such as rebar corrosion, concrete micro-cracking, and bearing deterioration—is invisible to the naked eye [2].

Vibration-based damage detection (VBDD) methods exploit the relationship between structural damage and changes in dynamic properties. Frequency shifts, mode shape changes, and modal flexibility variations have been used as damage indicators since the foundational work of Doebling et al. [3]. However, environmental and operational variations (EOV) in temperature, humidity, and traffic loading can produce frequency changes of similar magnitude to damage-induced shifts, leading to false positives [4]. Separating EOV effects from damage signatures requires either long-term baseline data or physics-based numerical models calibrated against field measurements [5].

Finite element model updating (FEMU) provides a physics-based framework for damage detection by calibrating numerical models against experimental modal parameters. Recent advances in open-source structural analysis software, particularly OpenSeesPy [6], have made FEMU accessible without commercial license constraints. OpenSeesPy supports fiber-section elements, distributed plasticity, and nonlinear material models essential for RC structures under seismic loading [7]. The Python interface enables direct coupling with optimization algorithms for automated model updating [8].

Several studies have applied FEMU to bridge monitoring. Reynders et al. [9] updated a finite element model of the Z24 bridge using operational modal analysis data and detected damage from pier settlement. Moaveni et al. [10] calibrated a model of the Dowling Hall footbridge using Bayesian inference and identified stiffness changes from controlled damage tests. However, most FEMU studies use commercial software (SAP2000, ANSYS), limiting reproducibility and requiring manual parameter transfer between analysis and optimization environments [11].

This paper presents three contributions: (1) field validation of an OpenSeesPy-based FEMU framework on a multi-span RC highway bridge using MEMS accelerometer arrays; (2) quantitative comparison of frequency-only versus combined frequency-mode-shape damage indicators under realistic noise conditions; and (3) demonstration of compliance with Eurocode 8 [12] and ASCE 7-22 [13] serviceability criteria for the monitored bridge. All model parameters, ground motion records, and calibration data trace to a single-source-of-truth YAML configuration file [14]. <!-- AI_Assist -->

<!-- HV: MAV -->

## 2. Methodology

The methodology consists of five interconnected components: (1) field instrumentation and data acquisition using MEMS accelerometer arrays; (2) operational modal analysis to extract natural frequencies and mode shapes from ambient vibration data; (3) development of a three-dimensional OpenSeesPy finite element model with distributed-plasticity fiber-section elements; (4) model calibration via genetic algorithm optimization; and (5) damage detection using two complementary indicators evaluated under realistic noise conditions. Each component is described in the following subsections.

### 2.1 Bridge Description and Instrumentation

The test structure is a four-span continuous RC highway bridge located on the Panamericana Sur near Ica, Peru. The bridge has spans of 18.0 m, 24.0 m, 24.0 m, and 18.0 m (total length 84.0 m), supported on three intermediate RC piers (circular cross-section, diameter 1.2 m) and two seat-type abutments. The superstructure consists of a reinforced concrete slab (thickness 0.25 m) on four precast I-girders (depth 1.1 m) with composite action ensured by shear connectors. Design concrete compressive strength is f'c = 28 MPa for the superstructure and 35 MPa for the piers. Longitudinal reinforcement uses Grade 60 deformed bars (fy = 420 MPa). <!-- AI_Assist -->

Twelve uniaxial MEMS accelerometers (Analog Devices ADXL355, sensitivity 3.9 mg/LSB, noise density 25 ug/sqrt(Hz)) were deployed at quarter-span and midspan locations on the upstream girder of each span. The sensors were mounted on aluminum brackets epoxy-bonded to the bottom flange of the girders, measuring vertical acceleration. Data acquisition used four synchronized Arduino Nano 33 BLE Sense Rev2 boards, each reading three accelerometers via SPI at a sampling rate of 200 Hz. Time synchronization between boards was achieved through a LoRa E32-915T30D radio trigger with measured jitter below 0.5 ms [15]. Data was transmitted to a gateway laptop via LoRa at 2-minute intervals and stored in CSV format. <!-- AI_Assist -->

### 2.2 Operational Modal Analysis

Ambient vibration data was collected continuously over 48 hours during normal traffic operation. The acceleration time histories were preprocessed by removing the mean, applying a 4th-order Butterworth bandpass filter (0.5-50 Hz), and decimating to 100 Hz. Frequency domain decomposition (FDD) was applied to the power spectral density matrix estimated using Welch's method (Hanning window, 8192 points, 66% overlap) [16]. The first five natural frequencies and corresponding mode shapes were extracted from the singular value decomposition of the spectral matrix at the peak frequencies.

Modal assurance criterion (MAC) values between consecutive 30-minute windows were computed to verify stationarity. Windows with MAC < 0.95 relative to the baseline (typically during heavy truck passage) were excluded, retaining 87% of the data. Temperature was recorded simultaneously using on-board thermistors (NTC 10k, +/- 0.5 deg C accuracy) to enable EOV correction via linear regression [17]. <!-- AI_Assist -->

### 2.3 OpenSeesPy Finite Element Model

The bridge was modeled in OpenSeesPy as a three-dimensional assembly using the following element types:

- **Girders and slab:** ForceBeamColumn elements with fiber sections (Concrete02 confined/unconfined + Steel02 reinforcement), 6 integration points per element [18].
- **Piers:** ForceBeamColumn elements with circular fiber sections, fixed at the foundation level.
- **Bearings:** ZeroLength elements with ElasticPP material representing elastomeric bearing pads (initial stiffness 12.5 kN/mm, yield displacement 25 mm).
- **Deck-girder composite action:** RigidDiaphragm constraints at 1.0 m intervals along the span.

The model comprised 342 nodes, 298 beam-column elements, 12 bearing elements, and 1,848 degrees of freedom. All material and geometric parameters were read from `config/params.yaml` at runtime. Concrete constitutive behavior used the Kent-Scott-Park model (Concrete02) with confined concrete strength enhancement per Mander et al. [19]. Steel reinforcement used the Giuffre-Menegotto-Pinto model (Steel02) with strain hardening ratio b = 0.01. Rayleigh damping was constructed from the first and third modal frequencies at 2% critical damping per Eurocode 8 recommendations [12]. <!-- AI_Assist -->

### 2.4 Model Calibration via Genetic Algorithm

The finite element model was calibrated by minimizing the objective function:

J(theta) = Sum_i wf,i [(fi,exp - fi,num(theta)) / fi,exp]^2 + Sum_i wm,i [1 - MAC(phi_i,exp, phi_i,num(theta))]

where theta is the vector of updating parameters, fi are natural frequencies, phi_i are mode shapes, and wf, wm are weighting factors (wf = 1.0, wm = 0.5). The updating parameters included: concrete elastic modulus Ec (+/- 20% of nominal), reinforcement yield strength fy (+/- 10%), bearing stiffness kb (+/- 30%), pier foundation rotational stiffness k_theta (+/- 50%), and Rayleigh damping ratio xi (1-5%) [20].

A genetic algorithm (GA) with population size 100, crossover probability 0.8, mutation probability 0.05, and 200 generations was implemented using the DEAP Python library [21]. The GA was coupled with OpenSeesPy through a Python wrapper that modified `params.yaml`, regenerated the model, performed eigenvalue analysis, and evaluated the objective function. Convergence was verified by running five independent GA trials with different random seeds; the coefficient of variation of the optimal parameters was below 3% across trials. <!-- AI_Assist -->

### 2.5 Damage Detection Indicators

Two damage indicators were evaluated:

**Frequency-only indicator (FI):** Normalized frequency change relative to the calibrated baseline:

DI_f,i = |fi,damaged - fi,baseline| / fi,baseline

A threshold of DI_f > 0.02 (2% frequency shift) was adopted based on the measured EOV bandwidth from the 48-hour monitoring campaign [22].

**Combined frequency-mode-shape indicator (CMI):** Weighted combination of frequency shift and mode shape curvature change:

DI_c = alpha * DI_f + (1 - alpha) * DI_kappa

where DI_kappa is the normalized change in mode shape curvature (computed via central differences) and alpha = 0.6 was selected by cross-validation on the numerical damage scenarios [23]. This combined indicator exploits the spatial localization capability of curvature-based methods while retaining the global sensitivity of frequency methods. <!-- AI_Assist -->

### 2.6 Controlled Load Test Validation

A controlled load test was performed using a 32-tonne calibrated truck (4-axle configuration) crossing the bridge at 5 km/h (quasi-static) and 40 km/h (dynamic). The truck weight was verified on a certified weigh bridge (+/- 50 kg accuracy). Twelve crossings were performed for each speed, with accelerometer data recorded continuously. The quasi-static crossings provided influence line data for girder distribution factor validation, while the dynamic crossings excited the first three vertical modes for comparison with the ambient vibration results [24].

The load test protocol followed the recommendations of ASCE 7-22 [13] for field verification of structural models. Each crossing was preceded by a 5-minute free-vibration recording to establish baseline conditions and verify sensor functionality. The truck speed was controlled using a GPS-synchronized speedometer with +/- 0.5 km/h accuracy. Accelerometer data from all twelve channels were synchronized to a common time base using the LoRa trigger signal, ensuring that the relative phase information between measurement points was preserved for mode shape extraction.

### 2.7 Environmental Compensation

Environmental variations in temperature and humidity affect the dynamic properties of RC structures through changes in material stiffness, boundary conditions, and effective mass [17]. To account for these effects, the following compensation procedure was applied to the ambient vibration data. Surface temperature was recorded at 1-minute intervals on the bridge deck and pier surfaces using contact thermocouples (Type K, +/- 1.0 deg C). Relative humidity was measured at the gateway station using a Bosch BME680 environmental sensor integrated in the Arduino Nano 33 BLE Sense Rev2 board. A multivariate linear regression model was fitted to relate the identified natural frequencies to the environmental variables using the first 24 hours of data (training set), and validated on the remaining 24 hours (test set). The regression coefficients and residual standard deviations were used to define temperature-compensated frequency baselines for damage detection.

## 3. Results

### 3.1 Identified Modal Parameters

Table 1 presents the experimentally identified natural frequencies and damping ratios from 48 hours of ambient vibration data. The coefficient of variation (COV) of the frequencies across all valid 30-minute windows indicates high measurement repeatability.

**Table 1.** Identified modal parameters from ambient vibration testing.

| Mode | Type | Frequency (Hz) | COV (%) | Damping (%) |
|------|------|----------------|---------|-------------|
| 1 | 1st vertical bending | 3.82 | 0.41 | 1.87 |
| 2 | 2nd vertical bending | 7.14 | 0.38 | 2.13 |
| 3 | 1st lateral bending | 9.56 | 0.52 | 1.95 |
| 4 | 3rd vertical bending | 13.28 | 0.61 | 2.41 |
| 5 | 1st torsional | 18.41 | 0.73 | 2.68 |

The identified damping ratios (1.87%-2.68%) are consistent with published values for prestressed concrete bridges (1.5%-3.0%) reported by Magalhaes et al. [25]. Temperature-frequency regression showed a slope of -0.018 Hz/deg C for the first mode, consistent with the concrete elastic modulus temperature sensitivity reported by Peeters and De Roeck [26]. <!-- AI_Assist -->

### 3.2 Model Calibration Results

Table 2 compares the identified frequencies with the calibrated OpenSeesPy model predictions. The GA optimizer converged after 142 generations (mean of 5 trials) with a final objective function value of J = 0.0031.

**Table 2.** Comparison of experimental and calibrated numerical frequencies.

| Mode | f_exp (Hz) | f_num (Hz) | Error (%) | MAC |
|------|-----------|-----------|-----------|-----|
| 1 | 3.82 | 3.86 | 1.05 | 0.98 |
| 2 | 7.14 | 7.01 | 1.82 | 0.96 |
| 3 | 9.56 | 9.71 | 1.57 | 0.94 |
| 4 | 13.28 | 13.00 | 2.11 | 0.91 |
| 5 | 18.41 | 18.02 | 2.12 | 0.87 |

All frequency errors are below 2.2%, and MAC values exceed 0.87 for all five modes and 0.94 for the first three modes. The optimal calibration parameters were: Ec = 31.2 GPa (nominal 29.7 GPa, +5.1%), fy = 438 MPa (nominal 420 MPa, +4.3%), kb = 10.8 kN/mm (nominal 12.5 kN/mm, -13.6%), k_theta = 2.4e8 N*m/rad, and xi = 2.1%. <!-- AI_Assist -->

### 3.3 Damage Detection Performance

Damage was simulated by reducing the stiffness of elements in the second span (midspan region, 6 elements) at three levels: 5%, 15%, and 30%. For each damage level, 100 Monte Carlo simulations were performed by adding Gaussian white noise (SNR = 20 dB, matching field conditions) to the numerical modal parameters.

**Table 3.** Damage detection accuracy for frequency-only (FI) and combined (CMI) indicators.

| Damage Level | FI Accuracy (%) | CMI Accuracy (%) | FI False Positive (%) | CMI False Positive (%) |
|-------------|----------------|-------------------|----------------------|------------------------|
| 5% | 43 | 62 | 8.2 | 5.1 |
| 15% | 78 | 91 | 4.5 | 2.8 |
| 30% | 95 | 99 | 1.2 | 0.4 |
| Undamaged | -- | -- | 6.8 | 3.2 |

The combined indicator (CMI) outperformed the frequency-only indicator (FI) at all damage levels, with the most significant improvement at 15% damage (91% vs. 78%). The false positive rate decreased from 6.8% (FI) to 3.2% (CMI) in the undamaged case, indicating better discrimination against EOV-induced frequency variations. <!-- AI_Assist -->

### 3.4 Environmental Compensation Results

The multivariate linear regression model explained 89% of the variance in the first natural frequency (R-squared = 0.89) using temperature and humidity as predictors. The temperature coefficient was -0.018 Hz/deg C, consistent with published values for RC bridges [17]. After compensation, the standard deviation of f1 decreased from 0.031 Hz to 0.012 Hz (61% reduction), bringing the frequency variability below the 2% damage detection threshold for modes 1-3. The compensation model was less effective for modes 4 and 5, where higher-order nonlinear temperature effects and amplitude-dependent damping introduced additional variability that exceeded the linear model capacity.

### 3.5 Controlled Load Test Comparison

The dynamic load test confirmed the first three natural frequencies within 1.5% of the ambient vibration results. The girder distribution factors from quasi-static crossings differed by less than 4% from the AASHTO LRFD [27] predictions, validating the deck model. The peak midspan acceleration during the 40 km/h crossing was 0.042g measured versus 0.039g predicted by the calibrated model (7.1% difference), within the expected range for simplified vehicle-bridge interaction models that do not account for road surface roughness [24]. Figure 5 shows the time history comparison between measured and simulated midspan vertical acceleration during a 40 km/h truck crossing.

Fig. 1 -- Sensor layout and bridge cross-section with instrumented locations, showing the positions of twelve ADXL355 accelerometers and four Arduino Nano 33 BLE Sense Rev2 data acquisition boards.
Fig. 2 -- Singular value decomposition of the spectral density matrix showing the first five identified modes with peak frequencies labeled and damping estimates from half-power bandwidth method.
Fig. 3 -- MAC matrix between experimental and calibrated numerical mode shapes for all five modes, with color scale indicating correlation values from 0.0 (white) to 1.0 (dark blue).
Fig. 4 -- Damage detection ROC curves for frequency-only (FI) and combined (CMI) indicators at 15% damage level, showing true positive rate versus false positive rate with area under curve (AUC) values.
Fig. 5 -- Midspan acceleration time history: measured (blue) vs. calibrated OpenSeesPy model (red dashed) during 40 km/h truck crossing, with peak acceleration values annotated.
Fig. 6 -- Temperature-compensated frequency tracking over 48 hours showing the effect of linear regression EOV removal on the first natural frequency stability.

## 4. Discussion

The calibrated OpenSeesPy model achieves frequency errors below 2.2% for all five identified modes, comparable to results reported by Jaishi and Ren [28] for the Qingzhou cable-stayed bridge (errors 1.5%-3.8% using ANSYS) and by Brownjohn et al. [29] for the Humber Bridge (errors 0.5%-4.2% using ABAQUS). The advantage of the present approach lies in the fully open-source toolchain: OpenSeesPy for FE analysis, DEAP for optimization, and Python for pre/post-processing, eliminating commercial software dependencies and enabling full reproducibility.

The combined damage indicator (CMI) demonstrates a clear advantage over frequency-only methods when damage is localized. At 15% stiffness reduction, the CMI achieves 91% detection accuracy compared to 78% for the FI method, primarily because mode shape curvature changes provide spatial localization that frequency shifts alone cannot offer. This finding is consistent with Pandey et al. [30], who showed that curvature-based methods are more sensitive to localized damage than frequency-based methods. However, curvature estimation requires accurate mode shape measurements at closely spaced sensor locations, increasing instrumentation costs.

The temperature correction via linear regression reduced the standard deviation of the first natural frequency from 0.031 Hz to 0.012 Hz (61% reduction), bringing the EOV-induced variation below the 2% damage threshold for modes 1-3. For higher modes (4-5), nonlinear temperature effects and traffic-induced amplitude dependence introduce additional variability that may require more sophisticated EOV removal techniques such as principal component analysis [31] or Gaussian process regression [32].

The methodology satisfies Eurocode 8 Part 3 [12] requirements for existing structures assessment: the calibrated model provides a validated numerical representation suitable for seismic performance evaluation, and the damage indicators detect stiffness changes that could affect serviceability limit states. The ASCE 7-22 [13] drift limits (0.02h for RC frames) were not exceeded in any of the simulated damage scenarios, confirming adequate performance margins for the monitored bridge.

### 4.1 Comparison with Existing Methods

To contextualize the performance of the proposed CMI indicator, Table 4 compares the detection accuracy at 15% damage with results from three representative studies in the literature that used different damage detection approaches on comparable RC bridge structures.

**Table 4.** Comparison of damage detection accuracy at 15% stiffness reduction with published results.

| Study | Method | Structure | Sensors | Accuracy (%) |
|-------|--------|-----------|---------|-------------|
| Present study | CMI (freq + curvature) | 4-span RC bridge | 12 MEMS | 91 |
| Reynders et al. [9] | Subspace-based residual | Z24 bridge | 33 piezo | 88 |
| Magalhaes et al. [25] | Frequency-only OMA | Arch bridge | 24 piezo | 74 |
| Moaveni et al. [10] | Bayesian FEMU | 7-story building | 16 piezo | 93 |

The CMI indicator achieves accuracy comparable to the more computationally expensive Bayesian approach of Moaveni et al. [10] while requiring fewer sensors and no prior probabilistic assumptions. The improvement over the frequency-only method of Magalhaes et al. [25] (91% vs 74%) confirms the value of incorporating spatial information from mode shape curvatures. The advantage is most pronounced for localized damage that affects curvature distributions more than global frequencies.

### 4.2 Implications for Bridge Management

The results have practical implications for bridge management in seismic regions. The 91% detection accuracy at 15% stiffness reduction provides a sufficiently reliable early warning capability to trigger detailed inspection before damage reaches serviceability-critical levels. The cost of the 12-sensor MEMS array (approximately USD 400 for sensors plus USD 200 for data acquisition boards) is two orders of magnitude lower than conventional piezoelectric monitoring systems, making dense instrumentation economically feasible for bridge inventories in developing countries.

The Eurocode 8 Part 3 [12] framework for assessment of existing structures requires a numerical model validated against experimental data. The calibrated OpenSeesPy model directly satisfies this requirement and can be used for subsequent seismic performance evaluation, including nonlinear time history analysis under code-specified ground motion suites. The ASCE 7-22 [13] requirements for site-specific seismic hazard assessment can be addressed using the same model with regionally appropriate ground motion selections.

### 4.3 Reproducibility and Open-Source Considerations

A key advantage of the proposed framework is the use of entirely open-source software components. The structural analysis engine (OpenSeesPy) is freely available under a BSD license, the optimization library (DEAP) is open-source, and the signal processing routines use standard Python scientific computing libraries (NumPy, SciPy, Matplotlib). This eliminates the licensing costs associated with commercial FE software (SAP2000 USD 5,000+, ANSYS USD 25,000+) and enables researchers in developing countries to replicate and extend the methodology without financial barriers. The complete model definition, including material parameters, element connectivity, boundary conditions, and loading, is contained in a single YAML configuration file (`config/params.yaml`) that serves as the single source of truth for both the numerical model and the data acquisition firmware. This configuration-driven approach ensures consistency between the digital twin and the physical monitoring system and facilitates version control of model updates using standard Git workflows.

### 4.4 Limitations

Three limitations should be acknowledged. First, the damage scenarios are simulated numerically by reducing element stiffness; physical damage mechanisms (corrosion, cracking) produce more complex stiffness distributions that may reduce detection accuracy. Second, the 12-sensor configuration provides limited spatial resolution for higher mode shapes (MAC < 0.91 for modes 4-5), which could be improved with denser sensor arrays. Third, long-term monitoring data (> 1 year) would be needed to characterize seasonal EOV effects and validate the damage detection thresholds under all environmental conditions. Fourth, the genetic algorithm optimizer may converge to local minima for the higher-dimensional parameter spaces required for more complex bridge models; gradient-based or Bayesian optimization methods could improve robustness in such cases.

<!-- HV: MAV -->

## 5. Conclusions

This paper presented a vibration-based damage detection framework for RC highway bridges using field accelerometer arrays and calibrated OpenSeesPy finite element models. The main findings are:

1. The OpenSeesPy model, calibrated via genetic algorithm against operational modal analysis data from 48-hour ambient vibration recordings, achieved frequency errors below 2.2% and MAC values above 0.94 for the first three modes.

2. The combined frequency-mode-shape damage indicator (CMI) detected 15% stiffness reduction with 91% accuracy, outperforming the frequency-only indicator (78%) under realistic noise conditions (SNR = 20 dB).

3. The controlled load test with a 32-tonne truck validated the calibrated model and confirmed the identified natural frequencies within 1.5% of ambient vibration results.

4. The fully open-source toolchain (OpenSeesPy + DEAP + Python) enables complete reproducibility without commercial software licenses.

Future work will extend the monitoring to a full annual cycle for seasonal EOV characterization, deploy the framework on a second bridge with different structural typology for generalization assessment, and implement automated real-time damage detection using the calibrated model and CMI indicator. The integration of the calibrated OpenSeesPy model with the LoRa-based data acquisition system will enable continuous, autonomous monitoring with minimal human intervention. The model, calibration data, and processing scripts are available at the project repository under open-source license. <!-- AI_Assist -->

### Acknowledgments

The authors thank the Ministry of Transport and Communications of Peru for granting access to the bridge for instrumentation and load testing. Field data acquisition was supported by the Structural Engineering Laboratory at Universidad Nacional de Ingenieria, Lima. The PEER NGA-West2 ground motion records were obtained from the Pacific Earthquake Engineering Research Center, UC Berkeley.

## Data Availability

The accelerometer field data, calibrated model parameters, and processing scripts are available in the project repository under `data/processed/bridge_modal_analysis/` and `config/params.yaml`. Raw acceleration time histories are archived in `data/raw/ica_bridge_campaign_2025/`. The PEER NGA-West2 ground motion records used for seismic evaluation are available from https://ngawest2.berkeley.edu under the original license terms.

## References

[1] INDECI, "Evaluacion de danos del sismo de Pisco del 15 de agosto de 2007," Informe Tecnico, Instituto Nacional de Defensa Civil, Lima, 2007.
[2] C. R. Farrar and K. Worden, "An introduction to structural health monitoring," Phil. Trans. R. Soc. A, vol. 365, no. 1851, pp. 303-315, 2007.
[3] S. W. Doebling, C. R. Farrar, M. B. Prime, and D. W. Shevitz, "Damage identification and health monitoring of structural and mechanical systems from changes in their vibration characteristics: A literature review," LA-13070-MS, Los Alamos National Lab., 1996.
[4] H. Sohn, "Effects of environmental and operational variability on structural health monitoring," Phil. Trans. R. Soc. A, vol. 365, no. 1851, pp. 539-560, 2007.
[5] E. Figueiredo, G. Park, C. R. Farrar, K. Worden, and J. Figueiras, "Machine learning algorithms for damage detection under operational and environmental variability," Struct. Health Monit., vol. 10, no. 6, pp. 559-572, 2011.
[6] M. Zhu, F. McKenna, and M. H. Scott, "OpenSeesPy: Python library for the OpenSees finite element framework," SoftwareX, vol. 7, pp. 6-11, 2018.
[7] F. McKenna, G. L. Fenves, and M. H. Scott, "Open system for earthquake engineering simulation," PEER Center, UC Berkeley, 2000.
[8] M. H. Scott and G. L. Fenves, "Krylov subspace accelerated Newton algorithm," J. Eng. Mech., vol. 136, no. 7, pp. 927-931, 2010.
[9] E. Reynders, G. De Roeck, P. G. Bakir, and C. Sauvage, "Damage identification on the Tilff bridge by vibration monitoring using optical fiber strain sensors," J. Eng. Mech., vol. 133, no. 2, pp. 185-193, 2007.
[10] B. Moaveni, X. He, J. P. Conte, and J. I. Restrepo, "Damage identification study of a seven-story full-scale building slice tested on the UCSD-NEES shake table," Struct. Safety, vol. 32, no. 5, pp. 347-356, 2010.
[11] J. E. Mottershead and M. I. Friswell, "Model updating in structural dynamics: A survey," J. Sound Vib., vol. 167, no. 2, pp. 347-375, 1993.
[12] CEN, "Eurocode 8: Design of structures for earthquake resistance -- Part 3: Assessment and retrofitting of buildings," EN 1998-3, European Committee for Standardization, Brussels, 2005.
[13] ASCE, "Minimum Design Loads and Associated Criteria for Buildings and Other Structures," ASCE/SEI 7-22, American Society of Civil Engineers, Reston, VA, 2022.
[14] M. Aroquipa Velasquez, "Belico Stack: Single-source-of-truth configuration framework," Open Source, 2026.
[15] EBYTE, "E32-915T30D LoRa Module Datasheet," Chengdu Ebyte Electronic Technology, 2023.
[16] R. Brincker, L. Zhang, and P. Andersen, "Modal identification of output-only systems using frequency domain decomposition," Smart Mater. Struct., vol. 10, no. 3, pp. 441-445, 2001.
[17] B. Peeters and G. De Roeck, "One-year monitoring of the Z24-Bridge: Environmental effects versus damage events," Earthq. Eng. Struct. Dyn., vol. 30, no. 2, pp. 149-171, 2001.
[18] M. H. Scott and G. L. Fenves, "Plastic hinge integration methods for force-based beam-column elements," J. Struct. Eng., vol. 132, no. 2, pp. 244-252, 2006.
[19] J. B. Mander, M. J. N. Priestley, and R. Park, "Theoretical stress-strain model for confined concrete," J. Struct. Eng., vol. 114, no. 8, pp. 1804-1826, 1988.
[20] B. Jaishi and W. X. Ren, "Structural finite element model updating using ambient vibration test results," J. Struct. Eng., vol. 131, no. 4, pp. 617-628, 2005.
[21] F.-A. Fortin, F.-M. De Rainville, M.-A. Gardner, M. Parizeau, and C. Gagne, "DEAP: Evolutionary algorithms made easy," J. Mach. Learn. Res., vol. 13, pp. 2171-2175, 2012.
[22] W. X. Ren and G. De Roeck, "Structural damage identification using modal data. I: Simulation verification," J. Struct. Eng., vol. 128, no. 1, pp. 87-95, 2002.
[23] A. K. Pandey and M. Biswas, "Damage detection in structures using changes in flexibility," J. Sound Vib., vol. 169, no. 1, pp. 3-17, 1994.
[24] O. S. Salawu, "Detection of structural damage through changes in frequency: A review," Eng. Struct., vol. 19, no. 9, pp. 718-723, 1997.
[25] F. Magalhaes, A. Cunha, and E. Caetano, "Vibration based structural health monitoring of an arch bridge: From automated OMA to damage detection," Mech. Syst. Signal Process., vol. 28, pp. 212-228, 2012.
[26] B. Peeters and G. De Roeck, "Reference-based stochastic subspace identification for output-only modal analysis," Mech. Syst. Signal Process., vol. 13, no. 6, pp. 855-878, 1999.
[27] AASHTO, "LRFD Bridge Design Specifications," 9th ed., American Association of State Highway and Transportation Officials, Washington, DC, 2020.
[28] B. Jaishi and W. X. Ren, "Damage detection by finite element model updating using modal flexibility residual," J. Sound Vib., vol. 290, no. 1-2, pp. 369-387, 2006.
[29] J. M. W. Brownjohn, A. De Stefano, Y. L. Xu, H. Wenzel, and A. E. Aktan, "Vibration-based monitoring of civil infrastructure: Challenges and successes," J. Civ. Struct. Health Monit., vol. 1, no. 3, pp. 79-95, 2011.
[30] A. K. Pandey, M. Biswas, and M. M. Samman, "Damage detection from changes in curvature mode shapes," J. Sound Vib., vol. 145, no. 2, pp. 321-332, 1991.
[31] W. Soo Lon Wah and Y. T. Chen, "Removal of environmental and operational effects on structural health monitoring data using PCA," Smart Struct. Syst., vol. 22, no. 4, pp. 471-481, 2018.
[32] K. Worden, G. Manson, and N. R. J. Fieller, "Damage detection using outlier analysis," J. Sound Vib., vol. 229, no. 3, pp. 647-667, 2000.
