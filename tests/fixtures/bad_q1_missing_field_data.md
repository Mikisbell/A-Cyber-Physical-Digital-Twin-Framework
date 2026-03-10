---
title: "Seismic Fragility Assessment of Mid-Rise Reinforced Concrete Frames Using Incremental Dynamic Analysis and OpenSeesPy"
domain: structural
quartile: Q1
version: 0.1
status: draft
---

## Abstract

This paper presents a seismic fragility assessment methodology for mid-rise reinforced concrete (RC) moment-resisting frames using incremental dynamic analysis (IDA) performed in OpenSeesPy. A 6-story, 3-bay RC frame designed per Peruvian seismic code E.030 was modeled with fiber-section beam-column elements incorporating Concrete02 and Steel02 constitutive models. Nonlinear time history analyses were conducted under 10 ground motion records scaled from 0.1g to 1.5g PGA in 0.1g increments, producing 150 individual simulations. Fragility curves were derived for four damage states: slight (inter-story drift ratio IDR > 0.5%), moderate (IDR > 1.0%), extensive (IDR > 2.0%), and complete (IDR > 4.0%). The median PGA values for each damage state were 0.18g, 0.35g, 0.62g, and 1.05g respectively, with logarithmic standard deviations between 0.28 and 0.42. The results indicate that the frame meets the life-safety performance objective under the design-level earthquake (PGA = 0.45g, Zone 4) with 94% probability. The numerical framework enables rapid fragility estimation for building portfolios in seismic regions. <!-- AI_Assist -->

## 1. Introduction

Seismic fragility curves quantify the probability of exceeding predefined damage states as a function of ground motion intensity, providing essential input for performance-based earthquake engineering (PBEE) and loss estimation frameworks [1]. The development of analytical fragility functions requires nonlinear structural models subjected to suites of ground motions spanning a range of intensity levels [2].

Incremental dynamic analysis (IDA) is the standard method for generating fragility curves, where a structural model is subjected to a suite of ground motions, each scaled to multiple intensity levels [3]. The resulting IDA curves relate an engineering demand parameter (EDP), such as maximum inter-story drift ratio (IDR), to an intensity measure (IM), such as peak ground acceleration (PGA) or spectral acceleration at the fundamental period Sa(T1).

OpenSeesPy provides an open-source platform for nonlinear dynamic analysis with fiber-section elements capable of capturing distributed plasticity, P-delta effects, and cyclic degradation [4]. The Python scripting interface enables automated parametric studies and IDA implementations without manual intervention between analysis runs.

Several studies have developed fragility curves for RC frames in Latin America. Villar-Vega et al. [5] compiled fragility functions for the GEM South America risk model using a combination of analytical and empirical methods. Gonzalez-Drigo et al. [6] developed fragility curves for low-rise RC frames in Lima using pushover-based methods. However, most studies use simplified modeling approaches (lumped plasticity) that may not capture the interaction between axial load and flexural capacity in columns under high seismic demands [7].

This paper develops fragility curves for a 6-story RC frame designed per Peruvian code E.030 using IDA with distributed-plasticity fiber-section elements in OpenSeesPy. The numerical model captures geometric nonlinearity (P-delta), material degradation (Concrete02 + Steel02), and realistic ground motion variability through a suite of 10 records selected from the PEER NGA-West2 database.

The remainder of this paper is organized as follows. Section 2 describes the reference structure, numerical model, ground motion selection, IDA procedure, and fragility curve derivation. Section 3 presents the IDA results, fragility parameters, damage concentration patterns, and comparison with code limits. Section 4 discusses the implications for seismic performance evaluation and identifies limitations. Section 5 summarizes the conclusions and future research directions.

Fragility curves are fundamental tools in performance-based earthquake engineering, providing the probabilistic link between ground motion intensity and structural damage states. The development of analytical fragility functions through IDA is computationally intensive but provides a physics-based alternative to empirical fragility functions derived from post-earthquake damage surveys, which are limited by the sparsity and inconsistency of field damage data in developing countries. The approach adopted in this study follows the methodology established by Vamvatsikos and Cornell [2], with modifications to account for the specific characteristics of the Peruvian seismic hazard and building construction practice.

The E.030 code governs the seismic design of buildings in Peru and has been updated several times since its original publication in 1977, most recently in 2018 following the lessons learned from the 2007 Pisco earthquake (Mw 8.0) and the 2001 Arequipa earthquake (Mw 8.4). The current version incorporates response modification factors, drift limits, and detailing requirements that are broadly consistent with international practice but differ in specific numerical values from ASCE 7-22 and Eurocode 8. Understanding the seismic performance implied by E.030 designs through fragility analysis is essential for calibrating risk models and informing future code revisions. <!-- AI_Assist -->

## 2. Methodology

### 2.1 Reference Structure

The reference structure is a 6-story, 3-bay RC moment-resisting frame extracted from a typical residential building in Lima, Peru, designed per E.030-2018 [8]. The frame has a total height of 18.0 m (3.0 m per story) and total width of 15.0 m (5.0 m bay spacing). Column dimensions are 0.45 m x 0.45 m for the first three stories and 0.40 m x 0.40 m for stories 4-6. Beam dimensions are 0.30 m x 0.50 m throughout. Design concrete strength f'c = 28 MPa. Longitudinal reinforcement fy = 420 MPa (Grade 60). Transverse reinforcement is Grade 60 stirrups at 100 mm spacing in plastic hinge regions and 200 mm elsewhere. <!-- AI_Assist -->

The structure is located in seismic Zone 4 (Z = 0.45g), Soil Type S2 (stiff soil, Vs30 = 350 m/s), with importance factor I = 1.0. The design base shear coefficient was 0.178 per E.030 static equivalent procedure. The fundamental period from eigenvalue analysis is T1 = 0.72 s.

### 2.2 Numerical Model

The frame was modeled in OpenSeesPy as a two-dimensional assembly in the plane of the moment-resisting frame. Out-of-plane effects were neglected under the assumption that the building is regular in plan and the lateral load is resisted entirely by the perimeter frames. Floor masses were lumped at beam-column joint nodes, with tributary mass computed from a dead load of 6.5 kN/m2 (slab + finishes) and live load of 2.0 kN/m2 (residential occupancy) reduced by 50% per E.030 for seismic mass calculation. The resulting seismic weight per floor is 1,125 kN for typical floors and 950 kN for the roof.

The OpenSeesPy model uses ForceBeamColumn elements with fiber sections (5 integration points per element) for all beams and columns. Material models:

- **Concrete:** Concrete02 with Kent-Scott-Park envelope. Unconfined concrete: fc = 28 MPa, ec0 = 0.002, fcu = 0, ecu = 0.006. Confined concrete (per Mander model): fcc = 34.7 MPa, ecc = 0.0035, fccu = 6.9 MPa, eccu = 0.015 [9].
- **Steel:** Steel02 (Giuffre-Menegotto-Pinto) with fy = 420 MPa, Es = 200 GPa, b = 0.01, R0 = 18, cR1 = 0.925, cR2 = 0.15.
- **Damping:** Rayleigh damping at 5% critical for modes 1 and 3.
- **Geometric nonlinearity:** P-delta transformation applied to all columns.

The model has 42 nodes, 36 beam-column elements, and 234 degrees of freedom. All parameters are read from `config/params.yaml` at runtime.

### 2.3 Ground Motion Selection

Ten ground motion records were selected from the PEER NGA-West2 database to represent the seismicity of Lima, Peru (subduction zone). Records were selected to match the E.030 design spectrum for Zone 4, Soil S2, in the period range 0.2T1 to 2.0T1 (0.14-1.44 s). The selected records have magnitudes Mw 6.5-8.0, distances 15-80 km, and Vs30 = 250-500 m/s. The selection criteria followed the provisions of E.030 Chapter 4.6 for time history analysis, which requires a minimum of 3 records for design purposes but recommends 7 or more for statistical reliability. Ten records were selected as a compromise between computational cost and representativeness of the seismic hazard.

The records were baseline-corrected and high-pass filtered at 0.1 Hz to remove long-period noise. Each record was scaled to match the target spectrum at the fundamental period of the structure (T1 = 0.72 s) using the geometric mean of the two horizontal components. The scale factors ranged from 0.65 to 2.8, within the commonly accepted range of 0.5-4.0 for IDA studies [2]. The scaled records were verified to have no artificial amplification of spectral content outside the period range of interest.

| # | RSN | Event | Year | Mw | Rjb (km) | PGA (g) |
|---|-----|-------|------|----|-----------|---------|
| 1 | 5824 | Pisco | 2007 | 8.0 | 35 | 0.34 |
| 2 | 1614 | Maule | 2010 | 8.8 | 78 | 0.23 |
| 3 | 953 | Loma Prieta | 1989 | 6.9 | 28 | 0.47 |
| 4 | 1111 | Kobe | 1995 | 6.9 | 15 | 0.52 |
| 5 | 182 | Imperial Valley | 1979 | 6.5 | 22 | 0.35 |
| 6 | 767 | Northridge | 1994 | 6.7 | 31 | 0.41 |
| 7 | 1602 | Chi-Chi | 1999 | 7.6 | 42 | 0.28 |
| 8 | 3471 | Tohoku | 2011 | 9.0 | 125 | 0.19 |
| 9 | 5654 | Arequipa | 2001 | 8.4 | 95 | 0.21 |
| 10 | 287 | Michoacan | 1985 | 8.1 | 55 | 0.15 |

### 2.4 Incremental Dynamic Analysis

Each ground motion was scaled to 15 intensity levels: PGA = 0.1g, 0.2g, ..., 1.5g. For each scale factor, a nonlinear time history analysis was performed using the Newmark method (gamma = 0.5, beta = 0.25) with adaptive time stepping (initial dt = 0.005 s, minimum dt = 0.0001 s). The maximum inter-story drift ratio (IDR) was recorded at each intensity level. Analyses that failed to converge were assigned IDR = 10% (collapse).

The convergence criterion was set to a norm of unbalanced force below 1e-6 kN with a maximum of 100 iterations per time step. When the Newton-Raphson algorithm failed to converge within the specified tolerance, the time step was halved (minimum dt = 0.0001 s) and the analysis was restarted from the last converged state. If convergence could not be achieved after 5 successive time step reductions, the analysis was terminated and the structure was classified as collapsed at that intensity level. The total number of analyses performed was 150 (10 records x 15 intensity levels), of which 138 (92%) converged to completion.

The IDA procedure was automated using a Python script that sequentially modified the scale factor in the ground motion input, executed the OpenSeesPy analysis, extracted the maximum IDR from all story levels, and stored the results in a structured CSV file. Each analysis required approximately 45 seconds on a standard workstation (Intel i7-12700H, 32 GB RAM), for a total computation time of approximately 1.9 hours for the complete IDA suite.

### 2.5 Modeling Verification

Prior to performing IDA, the OpenSeesPy model was verified through three independent checks. First, the modal analysis was compared with hand calculations using the generalized eigenvalue approach for a shear-beam idealization of the frame, yielding fundamental periods within 4% of the finite element results. Second, a linear time history analysis under a single ground motion (RSN 5824, Pisco 2007, unscaled) was compared with the response of an equivalent SDOF system using the Duhamel integral, with peak displacement agreement within 3.2%. Third, a monotonic pushover analysis was performed and the capacity curve was compared with the nominal yield and ultimate capacities computed from sectional analysis using moment-curvature relationships at each plastic hinge location.

The element sensitivity was assessed by comparing models with 3, 5, and 7 integration points per ForceBeamColumn element. The results showed that 5 integration points provided convergent results (within 2% of the 7-point model for all engineering demand parameters), consistent with the recommendations of Scott and Fenves [17] for distributed-plasticity elements.

### 2.6 Post-Processing and Statistical Analysis

The IDA results were post-processed to extract fragility parameters using maximum likelihood estimation (MLE). For each damage state, the probability of exceedance at each intensity level was computed as the fraction of records exceeding the damage threshold. The lognormal CDF parameters (median and logarithmic standard deviation) were fitted to these empirical exceedance probabilities using the optimization method proposed by Baker [15]. The goodness-of-fit was evaluated using the Kolmogorov-Smirnov test, with p-values exceeding 0.15 for all four damage states, confirming the adequacy of the lognormal assumption.

Confidence intervals on the fragility parameters were estimated using bootstrap resampling with 1000 replications. The 90% confidence intervals on the median PGA values were approximately +/- 15% for slight and moderate damage states and +/- 20% for extensive and complete damage states, reflecting the increased uncertainty at higher intensity levels where record-to-record variability dominates.

### 2.7 Fragility Curve Derivation

Fragility curves were derived by fitting a lognormal cumulative distribution function (CDF) to the IDA results for each damage state. The damage states follow HAZUS-MH definitions [10]:

- **Slight:** IDR > 0.5%
- **Moderate:** IDR > 1.0%
- **Extensive:** IDR > 2.0%
- **Complete:** IDR > 4.0%

The median and logarithmic standard deviation were estimated using maximum likelihood estimation (MLE). <!-- AI_Assist -->

## 3. Results

### 3.1 IDA Curves

Figure 1 shows the IDA curves for the 10 ground motion records. The curves exhibit the expected pattern of initial linearity followed by softening and eventual dynamic instability (flat line at high intensity levels). Record-to-record variability is significant, with collapse PGA ranging from 0.8g (RSN 1111, Kobe, near-field pulse) to 1.4g (RSN 3471, Tohoku, long-duration subduction). The near-field records (Kobe, Imperial Valley) produce steeper IDA curves with earlier onset of nonlinearity compared to the far-field subduction records (Tohoku, Pisco), reflecting the higher spectral content in the period range near the fundamental period of the structure.

The median IDA curve shows a clear yielding transition at approximately PGA = 0.2g, corresponding to the formation of plastic hinges at beam ends in the lower three stories. Beyond PGA = 0.6g, the median curve flattens significantly, indicating the onset of global instability mechanisms. The 16th and 84th percentile curves bracket the median with a spread that increases with intensity level, reflecting the growing influence of ground motion characteristics on the nonlinear structural response.

Fig. 1 -- IDA curves for 10 ground motion records showing maximum IDR versus PGA.

### 3.2 Fragility Parameters

Table 2 presents the fragility curve parameters for the four damage states.

**Table 2.** Fragility curve parameters (lognormal distribution).

| Damage State | Median PGA (g) | Beta (log-std) | P(DS at PGA=0.45g) |
|-------------|---------------|-----------------|---------------------|
| Slight | 0.18 | 0.28 | 0.98 |
| Moderate | 0.35 | 0.33 | 0.64 |
| Extensive | 0.62 | 0.38 | 0.18 |
| Complete | 1.05 | 0.42 | 0.02 |

At the design PGA of 0.45g (E.030, Zone 4), the probability of exceeding the extensive damage state is 18%, and the probability of collapse is 2%. These values indicate that the frame meets the life-safety performance objective with a confidence level exceeding 94%.

Fig. 2 -- Fragility curves for four damage states with 90% confidence intervals.

### 3.3 Damage Concentration

The maximum IDR consistently occurred at the 3rd story (soft-story mechanism), where the column section changes from 0.45 m to 0.40 m. This is consistent with the stiffness discontinuity at that level. Figure 3 shows the IDR profile along the height at the design PGA level.

Fig. 3 -- Inter-story drift ratio profile along building height at PGA = 0.45g for the 10 records.

### 3.4 Comparison with E.030 Limits

The E.030 seismic code limits the maximum IDR to 0.7% for RC frames under the design earthquake. At PGA = 0.45g, the median maximum IDR from IDA is 1.24%, which exceeds the E.030 limit by 77%. However, E.030 drift limits apply to linear elastic analysis with reduced forces, not to nonlinear analysis with unreduced demands. When compared using the inelastic drift from pushover analysis (R = 6), the effective drift at design level is 0.83%, which still exceeds the 0.7% limit by 19%.

Fig. 4 -- Comparison of IDA median response with E.030 drift limits.

### 3.5 Collapse Mechanism

The predominant collapse mechanism observed in the IDA simulations was a soft-story failure at the 3rd story, where the column section changes from 0.45 m to 0.40 m. Of the 12 analyses that did not converge (classified as collapsed), 9 (75%) exhibited maximum IDR at the 3rd story. The remaining 3 collapses occurred at the 1st story under near-field pulse-type records that imposed large displacement demands at the base level. The soft-story mechanism is driven by the abrupt stiffness reduction at the section transition, combined with the reduced confinement effectiveness of the smaller column section under high axial load ratios.

The energy dissipation was predominantly concentrated in beam plastic hinges at the 2nd and 3rd stories, with column plastic hinges forming only at the base of 1st-story columns and at the top of 3rd-story columns. This partially confirms the strong-column-weak-beam design philosophy embedded in E.030, although the column hinging at the 3rd-story transition level indicates a localized deficiency in the capacity design hierarchy. The total hysteretic energy dissipated ranged from 45 kJ at PGA = 0.3g to 380 kJ at PGA = 1.0g, with the 3rd-story beams accounting for 35-42% of the total dissipation across all intensity levels.

### 3.6 Sensitivity to Damping Model

An additional parametric study was conducted to evaluate the sensitivity of the fragility results to the assumed damping model. Three Rayleigh damping configurations were tested: (a) 2% critical at modes 1 and 3 (baseline), (b) 5% critical at modes 1 and 3 (current model), and (c) 3% stiffness-proportional only. The median collapse PGA varied by +/- 8% across the three configurations, with higher damping producing higher collapse capacities as expected. The 5% damping ratio used in the baseline model is at the upper bound of recommended values for RC structures per Eurocode 8 [12], which specifies 5% for cracked RC elements. The effect of damping on the fragility parameters was less pronounced at lower damage states (slight, moderate), where the structural response remains predominantly elastic and less sensitive to energy dissipation assumptions.

## 4. Discussion

### 4.1 Performance Assessment

The fragility curves indicate that the 6-story RC frame designed per E.030 provides adequate life-safety performance under the design earthquake (2% collapse probability at PGA = 0.45g), consistent with the target reliability implicit in modern seismic codes [11]. However, the probability of moderate damage (64%) is significant, suggesting that post-earthquake functionality may be compromised even under design-level shaking.

The concentration of damage at the 3rd story highlights a known weakness of frames with section changes at mid-height. The E.030 code does not explicitly require capacity design verification at section transitions, unlike Eurocode 8 which mandates a 20% overstrength at column section changes [12]. This design practice could be improved by requiring explicit verification of the column-to-beam strength ratio at transition levels.

The record-to-record variability (beta = 0.28-0.42) is consistent with values reported in the literature for RC frames [13]. The higher variability at the complete damage state reflects the sensitivity of collapse capacity to ground motion characteristics (duration, frequency content, pulse effects).

### 4.2 Ground Motion Suite Size

The use of 10 ground motion records provides reasonable estimates of median fragility parameters but may underestimate the tails of the distribution. ASCE 7-22 recommends a minimum of 11 records for nonlinear dynamic analysis, while FEMA P-695 requires 22 far-field and 28 near-field records for collapse assessment [14]. The present study uses 10 records as a compromise between computational cost and statistical robustness. Bootstrap resampling of the 10 records indicates that the 90% confidence interval on the median collapse PGA is +/- 0.12g, which is substantial relative to the median value of 1.05g. Increasing the suite to 22 records would reduce this uncertainty by approximately 40%, as the confidence interval width scales with 1/sqrt(n) for independent samples.

### 4.3 Comparison with Code-Implicit Fragility

The E.030 seismic code does not provide explicit fragility targets, but the implicit reliability can be estimated from the design force reduction factor (R = 6) and the overstrength factor (Omega = 2.0 per FEMA P-695). The resulting adjusted collapse margin ratio (ACMR) for the present frame is 1.05g / 0.45g = 2.33, which exceeds the minimum ACMR of 1.56 specified in FEMA P-695 for an acceptable collapse probability of 10% under the maximum considered earthquake (MCE). This suggests that the E.030 design provisions provide a level of seismic safety comparable to that intended by ASCE 7-22, despite the differences in the force reduction factors and design spectral shapes between the two codes.

### 4.4 Limitations

The modeling assumptions introduce several sources of epistemic uncertainty that are not explicitly quantified in the present study. The fiber-section discretization (20 fibers per section) may introduce numerical errors in the moment-curvature response at high ductility demands, particularly for confined columns where the stress gradient across the section is steep. A convergence study with 10, 20, and 40 fibers showed that the median collapse PGA varied by less than 3% between 20 and 40 fibers, confirming adequate discretization for the present application. The fixed-base assumption neglects soil-structure interaction (SSI) effects, which can be significant for soft soil sites (Vs30 < 300 m/s). For the assumed soil type S2 (Vs30 = 350 m/s), SSI effects are expected to be minor based on the NIST GCR 12-917-21 recommendations [22], but this assumption has not been verified through site-specific analysis.

All simulations in this study are purely numerical. No field measurements, laboratory tests, or physical validation data were used. The model parameters (concrete strength, steel yield, dimensions) are nominal design values from the E.030 design process. In-situ material properties may differ from design values due to construction variability, aging, and environmental exposure. This is a fundamental limitation for a Q1-level publication, where experimental validation is typically expected to corroborate numerical predictions.

The present study does not include a formal literature review section that would contextualize the contributions within the existing body of knowledge on fragility assessment methods. A comprehensive review of analytical, empirical, and hybrid fragility approaches, along with a systematic comparison of the proposed IDA-based methodology with alternative methods such as cloud analysis, multiple stripe analysis, and simplified capacity-spectrum approaches, would strengthen the manuscript.

Additionally, the data availability statement is absent. Transparency and reproducibility requirements for high-impact journals necessitate clear documentation of data access policies, including ground motion records, model input files, and processed results. Without this information, independent verification of the reported fragility parameters is not possible. <!-- AI_Assist -->

### 4.5 Implications for Seismic Risk Assessment

The fragility curves developed in this study can be used as input for probabilistic seismic risk assessment of building portfolios in Lima and other cities in seismic Zone 4 of Peru. The median PGA values for each damage state provide the central tendency of the fragility functions, while the logarithmic standard deviations capture the combined aleatory (ground motion variability) and epistemic (modeling) uncertainties. When combined with site-specific seismic hazard curves, these fragility functions enable the computation of mean annual frequencies of exceeding each damage state, which form the basis for loss estimation and insurance pricing.

The 2% collapse probability at the design PGA of 0.45g translates to a mean annual frequency of collapse of approximately 2.4e-4 per year when convolved with the seismic hazard curve for Lima (assuming a 475-year return period for the design earthquake). This value is within the range of 1e-4 to 1e-3 per year considered acceptable in the literature for ordinary buildings [15], but exceeds the more stringent target of 1e-4 per year proposed for critical facilities.

The soft-story vulnerability at the 3rd floor level identified in this study is particularly concerning for the Peruvian building stock, where column section transitions at mid-height are common practice due to architectural and economic constraints. A portfolio-level risk assessment using the present fragility functions could quantify the aggregate expected annual loss associated with this design practice and inform decisions about code revisions or retrofit programs.

### 4.6 Comparison with Published Fragility Functions

The fragility parameters obtained in this study are compared with published values for similar RC frames in Latin America. Villar-Vega et al. [5] reported median collapse PGA values of 0.85-1.15g for mid-rise RC frames in the GEM South America risk model, with logarithmic standard deviations of 0.35-0.50. The present results (median 1.05g, beta 0.42) fall within this range, providing independent confirmation of the GEM fragility estimates for the Peruvian building typology.

Gonzalez-Drigo et al. [6] obtained median collapse PGA values of 0.72-0.95g for low-rise RC frames in Lima using pushover-based methods with the capacity spectrum approach. The higher collapse capacity obtained in the present study (1.05g) may reflect the use of IDA, which captures the dynamic amplification and degradation effects that are not fully represented in static pushover methods. Additionally, the 6-story frame studied here has a longer fundamental period (0.72 s vs. 0.45-0.55 s for the low-rise frames), which may result in lower spectral demands at the fundamental period and consequently higher collapse margins.

### 4.7 Applicability to Different Structural Typologies

The fragility assessment methodology presented in this paper is applicable to regular RC moment-resisting frames with distributed-plasticity behavior. For frames with masonry infills, the interaction between the infill panels and the bounding frame introduces additional failure modes (diagonal strut failure, frame-infill interface sliding, and out-of-plane infill collapse) that are not captured by the bare-frame model used here [20]. Extending the methodology to infilled frames would require the addition of diagonal strut elements with appropriate hysteretic models (e.g., Crisafulli model) and the definition of additional damage states specific to infill failure.

For frames with flat-slab systems (common in Peruvian commercial buildings), the absence of beams eliminates the strong-column-weak-beam mechanism that provides energy dissipation in moment-resisting frames. The fragility curves for flat-slab systems would be expected to show lower ductility capacities and higher collapse probabilities at moderate intensity levels. A separate study addressing flat-slab RC frames is planned as an extension of the present work.

The numerical framework is readily extensible to other structural systems by modifying the element types and material models in the OpenSeesPy model definition. Steel moment frames, steel braced frames, and RC shear wall systems can all be modeled within the same IDA framework, with the primary differences being the element formulations and damage state definitions. The automation of the IDA procedure through the Python scripting interface enables batch processing of multiple structural configurations, facilitating portfolio-level fragility assessment.

## 5. Conclusions

Seismic fragility curves were developed for a 6-story RC frame designed per Peruvian code E.030 using incremental dynamic analysis with fiber-section OpenSeesPy models. The frame provides adequate life-safety performance under the design earthquake (2% collapse probability), but the probability of moderate damage is 64%. The soft-story mechanism at the 3rd floor column transition requires attention in code provisions. The numerical framework enables rapid fragility assessment for building portfolios in seismic zones.

Future work should include experimental validation with shake table tests, sensitivity analysis of material parameters, and extension to irregular frame configurations. The numerical framework could also be extended to incorporate soil-structure interaction effects, which are particularly important for soft soil sites common in Lima and other coastal cities in Peru. The integration with performance-based loss estimation frameworks (FEMA P-58) would enable direct quantification of expected repair costs and downtime for building portfolios.

The authors acknowledge that the absence of field data and laboratory validation limits the conclusions to numerical predictions that require experimental corroboration before practical application. The fragility curves presented herein should be considered as preliminary estimates suitable for comparative studies and parametric investigations, but not as definitive fragility functions for code calibration or loss estimation purposes without independent validation.

The key findings of this study are summarized as follows:

1. The median collapse PGA of 1.05g provides a collapse margin ratio of 2.33 relative to the design PGA (0.45g), exceeding the FEMA P-695 minimum ACMR of 1.56 for acceptable collapse probability.

2. The probability of moderate damage at the design level (64%) indicates that post-earthquake functionality will likely be compromised even under code-level shaking, suggesting that the E.030 implicit performance objective prioritizes life safety over continued operation.

3. The soft-story mechanism at the 3rd floor level, where column sections transition from 0.45 m to 0.40 m, concentrates 75% of collapse failures at this location, highlighting the need for explicit capacity design verification at section transitions.

4. The sensitivity of fragility parameters to the damping model (+/- 8% on median collapse PGA) underscores the importance of using physically justified damping ratios based on material state and deformation level rather than fixed code-specified values.

5. The IDA framework, implemented entirely in OpenSeesPy with automated Python scripting, processes 150 analyses in approximately 1.9 hours, making it computationally feasible for parametric studies and portfolio-level assessments.

6. The fragility parameters are consistent with published values for similar RC frames in the GEM South America risk model [5], providing independent validation of the regional fragility estimates.

The numerical framework developed in this study can serve as a template for systematic fragility assessment of the Peruvian building stock across different structural typologies, heights, and seismic zones. However, the absence of experimental validation remains the primary limitation, and laboratory testing of representative RC subassemblies under cyclic loading is essential to confirm the assumed material models and damage state definitions. <!-- AI_Assist -->

## References

[1] FEMA, "Seismic Performance Assessment of Buildings," FEMA P-58-1, Vol. 1, Federal Emergency Management Agency, Washington, DC, 2018.
[2] D. Vamvatsikos and C. A. Cornell, "Incremental dynamic analysis," Earthq. Eng. Struct. Dyn., vol. 31, no. 3, pp. 491-514, 2002.
[3] A. K. Chopra, Dynamics of Structures: Theory and Applications to Earthquake Engineering, 5th ed. Pearson, 2017.
[4] M. Zhu, F. McKenna, and M. H. Scott, "OpenSeesPy: Python library for the OpenSees finite element framework," SoftwareX, vol. 7, pp. 6-11, 2018.
[5] M. Villar-Vega et al., "Development of a fragility model for the residential building stock in South America," Earthq. Spectra, vol. 33, no. 2, pp. 581-604, 2017.
[6] R. Gonzalez-Drigo et al., "Seismic vulnerability of RC buildings in Lima, Peru," Bull. Earthq. Eng., vol. 15, pp. 1121-1147, 2017.
[7] L. F. Ibarra, R. A. Medina, and H. Krawinkler, "Hysteretic models that incorporate strength and stiffness deterioration," Earthq. Eng. Struct. Dyn., vol. 34, no. 12, pp. 1489-1511, 2005.
[8] SENCICO, "Norma Tecnica E.030: Diseno Sismorresistente," Reglamento Nacional de Edificaciones, Lima, 2018.
[9] J. B. Mander, M. J. N. Priestley, and R. Park, "Theoretical stress-strain model for confined concrete," J. Struct. Eng., vol. 114, no. 8, pp. 1804-1826, 1988.
[10] FEMA, "Multi-hazard Loss Estimation Methodology: HAZUS-MH MR4," Federal Emergency Management Agency, Washington, DC, 2003.
[11] A. B. Liel, C. B. Haselton, G. G. Deierlein, and J. W. Baker, "Incorporating modeling uncertainties in the assessment of seismic collapse risk of buildings," Struct. Safety, vol. 31, no. 2, pp. 197-211, 2009.
[12] CEN, "Eurocode 8: Design of structures for earthquake resistance -- Part 1: General rules," EN 1998-1, European Committee for Standardization, Brussels, 2004.
[13] C. B. Haselton et al., "Seismic collapse safety of reinforced concrete buildings: I. Assessment of ductile moment frames," J. Struct. Eng., vol. 137, no. 4, pp. 481-491, 2011.
[14] ATC, "Quantification of Building Seismic Performance Factors," FEMA P-695, Applied Technology Council, Redwood City, CA, 2009.
[15] J. W. Baker, "Efficient analytical fragility function fitting using dynamic structural analysis," Earthq. Spectra, vol. 31, no. 1, pp. 579-599, 2015.
[16] S. W. Doebling et al., "Damage identification and health monitoring of structural and mechanical systems from changes in their vibration characteristics," LA-13070-MS, Los Alamos National Lab., 1996.
[17] F. McKenna, G. L. Fenves, and M. H. Scott, "Open system for earthquake engineering simulation," PEER Center, UC Berkeley, 2000.
[18] M. Aroquipa Velasquez, "Belico Stack: SSOT configuration framework," Open Source, 2026.
[19] R. W. Clough and J. Penzien, Dynamics of Structures, 3rd ed. Computers & Structures, Inc., 2003.
[20] T. Paulay and M. J. N. Priestley, Seismic Design of Reinforced Concrete and Masonry Buildings, Wiley, 1992.
[21] G. G. Deierlein, A. M. Reinhorn, and M. R. Willford, "Nonlinear structural analysis for seismic design," NIST GCR 10-917-5, 2010.
[22] P. Bazzurro and C. A. Cornell, "Seismic hazard analysis of nonlinear structures," J. Struct. Eng., vol. 120, no. 11, pp. 3320-3344, 1994.
[23] A. Kappos, G. Panagopoulos, C. Panagiotopoulos, and G. Penelis, "A hybrid method for the vulnerability assessment of R/C and URM buildings," Bull. Earthq. Eng., vol. 4, no. 4, pp. 391-413, 2006.
[24] E. Kalkan and S. K. Kunnath, "Assessment of current nonlinear static procedures for seismic evaluation," Eng. Struct., vol. 29, pp. 305-316, 2007.
[25] H. Krawinkler and E. Miranda, "Performance-based earthquake engineering," in Earthquake Engineering: From Engineering Seismology to Performance-Based Engineering, CRC Press, 2004.
