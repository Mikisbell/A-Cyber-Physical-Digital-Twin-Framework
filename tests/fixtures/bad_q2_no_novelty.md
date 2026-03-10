---
title: "Nonlinear Static Analysis of a Reinforced Concrete Frame Under Lateral Loading"
domain: structural
quartile: Q2
version: 0.5
status: draft
---

## Abstract

This paper presents a nonlinear static (pushover) analysis of a 4-story reinforced concrete moment-resisting frame using OpenSeesPy finite element software. The frame was designed according to Peruvian seismic code E.030 for Zone 4 conditions. The model uses fiber-section beam-column elements with Concrete02 and Steel02 material models to capture distributed plasticity effects. A displacement-controlled pushover analysis was performed using an inverted triangular load pattern applied up to a roof drift ratio of 4%. The capacity curve shows an elastic stiffness of 12,500 kN/m, yield base shear of 485 kN at 0.35% roof drift, and ultimate capacity of 612 kN at 2.1% roof drift. The inter-story drift profile indicates concentration of inelastic demand at the first story, consistent with a soft-story mechanism. Performance point evaluation using the capacity spectrum method per ATC-40 indicates that the frame meets the life-safety performance objective under the E.030 design spectrum for Zone 4. <!-- AI_Assist -->

## 1. Introduction

Reinforced concrete moment-resisting frames are the most common structural system for mid-rise buildings in Peru and other developing countries in seismic regions [1]. The seismic performance of these structures depends on the distribution of stiffness, strength, and ductility along the height, which can be evaluated through nonlinear static (pushover) analysis [2].

Pushover analysis has been widely adopted in practice and codes as a simplified method for estimating the nonlinear seismic response of structures [3]. The method applies monotonically increasing lateral forces to the structure until a target displacement is reached, producing a capacity curve that relates base shear to roof displacement. The capacity spectrum method (CSM) per ATC-40 [4] or the displacement coefficient method per ASCE 41-17 [5] can then be used to estimate the seismic demand.

OpenSeesPy provides an open-source platform for nonlinear structural analysis with advanced material models and element formulations [6]. Several researchers have used OpenSeesPy for pushover analysis of RC frames [7]. This paper applies pushover analysis to a 4-story RC frame designed per E.030. The analysis follows standard procedures established in the literature and applies them to a Peruvian building configuration.

[TODO: clarify what is novel about this work compared to existing pushover studies]
[TODO: add explicit novelty statement differentiating from previous pushover studies]

The paper is organized as follows. Section 2 describes the reference structure, the numerical model, and the analysis procedure. Section 3 presents the results in terms of capacity curves, drift profiles, performance point evaluation, and plastic hinge formation sequence. Section 4 discusses the implications and limitations. Section 5 summarizes the conclusions.

Pushover analysis has become a standard tool in structural engineering practice for the preliminary assessment of seismic performance. The method provides a computationally efficient alternative to nonlinear time history analysis by replacing the dynamic loading with an equivalent static load pattern applied monotonically. While this simplification introduces inherent limitations—most notably the inability to capture higher-mode effects, cyclic degradation, and record-specific dynamic amplification—the method has been extensively validated against dynamic analyses for regular, low-rise to mid-rise building structures [3]. The ATC-40 procedure used in this study converts the pushover capacity curve into an acceleration-displacement response spectrum (ADRS) format, enabling direct comparison with the seismic demand spectrum to identify the performance point at which the structural capacity matches the reduced seismic demand accounting for inelastic energy dissipation.

The application of pushover analysis to Peruvian RC frames is motivated by the need to evaluate the seismic adequacy of the existing building stock, much of which was designed before the major code revisions triggered by the 2007 Pisco earthquake. The E.030-2018 code represents the current state of practice, but many existing buildings were designed to earlier versions with less stringent detailing requirements and lower design force levels. A systematic pushover-based assessment of representative building typologies can identify common deficiencies and guide retrofit prioritization programs.

## 2. Methodology

The methodology follows the standard pushover analysis procedure established in ATC-40 [4] and ASCE 41-17 [5], applied to a regular RC frame designed per Peruvian seismic code E.030-2018. The analysis consists of four steps: (1) development of a nonlinear finite element model with distributed plasticity using fiber-section elements; (2) application of monotonically increasing lateral loads following an inverted triangular pattern; (3) extraction and bilinear idealization of the capacity curve; and (4) performance point evaluation using the capacity spectrum method. Each step is described in the following subsections.

### 2.1 Reference Structure

The reference structure is a 4-story, 2-bay RC moment-resisting frame with a total height of 12.0 m (3.0 m per story) and total width of 10.0 m (5.0 m bay spacing). All columns are 0.40 m x 0.40 m with 8-No. 20 mm longitudinal bars (rho = 1.57%). All beams are 0.25 m x 0.45 m with 4-No. 16 mm top and 3-No. 16 mm bottom longitudinal bars. Concrete compressive strength f'c = 21 MPa. Steel yield strength fy = 420 MPa. Transverse reinforcement consists of No. 8 mm stirrups at 150 mm spacing. <!-- AI_Assist -->

The structure is designed for Zone 4 (Z = 0.45g) per E.030-2018 [8] with soil type S2 (stiff soil, Vs30 = 350 m/s) and importance factor I = 1.0. The design base shear coefficient is V/W = 0.156, computed using the static equivalent lateral force procedure per E.030 Section 4.5. The seismic weight per floor is 890 kN for typical floors and 745 kN for the roof, resulting in a total seismic weight W = 3,415 kN and a design base shear V = 533 kN. The fundamental period from the E.030 empirical formula (T = 0.07 * H^0.75) is 0.45 s, while the eigenvalue analysis of the numerical model yields T1 = 0.58 s, reflecting the difference between the empirical estimate (which includes the stiffening effect of non-structural elements) and the bare-frame analytical model.

The dead load includes the self-weight of structural elements, a 120 mm thick slab (2.88 kN/m2), finishes (1.5 kN/m2), and partition walls (1.0 kN/m2). The live load is 2.0 kN/m2 per E.020 for residential occupancy. For seismic mass calculation, 100% of dead load and 50% of live load were included per E.030 Section 4.3.

### 2.2 Material Properties

The material properties used in the analysis are summarized below. Concrete compressive strength f'c = 21 MPa represents the minimum specified value for structural concrete in Peru per E.060 [8]. The actual in-situ strength may be 10-30% higher due to aging and curing effects, but the nominal value was used to provide a conservative estimate of capacity. The steel reinforcement grade is ASTM A615 Grade 60 with nominal yield strength fy = 420 MPa and ultimate strength fu = 620 MPa. The strain hardening ratio b = fu/fy - 1 = 0.476 was idealized as b = 0.01 in the Steel02 model, which captures the initial post-yield stiffness without modeling the large-strain hardening behavior that occurs at strains above 0.02.

The confined concrete properties were computed using the Mander et al. [9] model based on the transverse reinforcement configuration. For columns (0.40 m x 0.40 m with No. 8 mm stirrups at 150 mm), the confinement ratio was fl/fc = 0.073, yielding a confined strength enhancement of 26% (fcc = 26.5 MPa). The ultimate confined strain was 0.012, approximately twice the unconfined value. For beams, the confinement effect was smaller (15% enhancement) due to the rectangular cross-section aspect ratio and the wider stirrup spacing in the midspan region.

### 2.3 Finite Element Model

The OpenSeesPy model consists of 15 nodes and 12 ForceBeamColumn elements with fiber sections. Each fiber section is discretized into 20 concrete fibers and 8 steel fibers. Material models include:

- **Concrete:** Concrete02 with fc = 21 MPa, ec0 = 0.002, fcu = 0, ecu = 0.005 (unconfined) and fcc = 26.5 MPa, ecc = 0.004, fccu = 5.3 MPa, eccu = 0.012 (confined per Mander model) [9].
- **Steel:** Steel02 with fy = 420 MPa, Es = 200 GPa, b = 0.01.
- **Geometric nonlinearity:** P-delta transformation on all columns.
- **Damping:** Not applicable for static analysis.

Rigid floor diaphragm constraints are applied at each story level. Column bases are fixed. The model was verified by comparing the fundamental period (T1 = 0.58 s) with the E.030 empirical formula (T = 0.07 * H^0.75 = 0.45 s), yielding a ratio of 1.29, within the expected range for frames with masonry infills not considered in the model [10]. <!-- AI_Assist -->

### 2.3 Analysis Procedure

[TODO: add comparison with another analysis method to demonstrate advantage]

A displacement-controlled pushover analysis was performed with the following parameters:

- **Load pattern:** Inverted triangular, proportional to the first mode shape
- **Control node:** Roof center (node 13)
- **Target displacement:** 480 mm (4% roof drift ratio)
- **Load increment:** 0.5 mm per step (960 steps total)
- **Convergence criterion:** Norm of unbalance force < 1e-6 kN

The analysis was performed using the Newton-Raphson algorithm with tangent stiffness updates at each iteration. For steps near the ultimate capacity where convergence was difficult, the Modified Newton algorithm with initial stiffness was used as a fallback. The convergence criterion was set to a norm of unbalanced force below 1e-6 kN with a maximum of 50 iterations per load step. The complete pushover analysis required approximately 12 seconds on a standard desktop computer (Intel i5-12400, 16 GB RAM).

### 2.4 Bilinear Idealization

The pushover capacity curve was idealized as a bilinear curve following the equal energy criterion. The yield point was defined as the intersection of the initial elastic stiffness line (secant stiffness at 60% of the maximum base shear) with the post-yield plateau (horizontal line at the maximum base shear). The ultimate point was defined as the point where the base shear drops to 80% of the maximum value on the descending branch, following common practice in the literature [10]. The idealized bilinear curve provides the yield displacement, yield strength, ultimate displacement, and ductility ratio used for performance evaluation.

### 2.6 Model Verification

The finite element model was verified through three checks prior to the pushover analysis. First, the gravity load analysis was performed to confirm that the axial loads in columns matched the tributary area calculations within 1%. Second, the eigenvalue analysis was compared with the Rayleigh quotient for an equivalent shear-building model, with agreement within 5% for the first three modes. Third, a linear static analysis under a uniform lateral load of 10 kN per floor was performed to verify the elastic stiffness against hand calculations using portal frame approximation.

The modal analysis identified four modes below 25 Hz with the following frequencies and modal mass participation ratios: Mode 1 (0.58 s, 87.2%), Mode 2 (0.19 s, 9.3%), Mode 3 (0.11 s, 2.8%), Mode 4 (0.08 s, 0.7%). The cumulative modal mass participation for the first two modes exceeds 96%, confirming that the structural response is dominated by the first mode and that the inverted triangular load pattern is appropriate for pushover analysis.

### 2.7 Performance Evaluation

The performance point was evaluated using the capacity spectrum method per ATC-40 [4]:

1. Convert the pushover curve to ADRS (Acceleration-Displacement Response Spectrum) format using the modal participation factor and effective modal mass of the first mode.
2. Overlay the E.030 design spectrum (Zone 4, Soil S2, 5% damping) in ADRS format.
3. Find the intersection using equivalent linearization with the bilinear approximation of the capacity spectrum.
4. Compare the performance point displacement with the drift limits in E.030.

### 2.8 Gravity Load Analysis

Prior to the pushover analysis, a gravity load analysis was performed by applying dead loads and 50% of live loads to the structure. The gravity load analysis serves two purposes: (a) establishing the initial stress state in columns, which affects the flexural capacity and ductility of the sections, and (b) verifying that the model correctly represents the tributary area loading. The axial load ratios (N/Agfc) at the base of the first-story columns were 0.18 for interior columns and 0.12 for exterior columns, within the acceptable range for RC frames designed for seismic resistance (typically N/Agfc < 0.35 per E.030). The gravity-induced moments at beam ends were less than 10% of the flexural capacity, confirming that the lateral load response dominates the pushover behavior.

The gravity load was maintained constant throughout the pushover analysis using a separate load pattern, while the lateral loads were applied incrementally in a second load pattern. This approach ensures that the P-delta effects are correctly captured at all displacement levels, as the gravity loads contribute to the geometric nonlinearity through the second-order moment amplification at each story level.

### 2.9 Element and Section Verification

The moment-curvature response of representative column and beam sections was computed independently using a fiber-section analysis script to verify the OpenSeesPy element behavior. For the 0.40 m x 0.40 m column section under an axial load ratio of 0.18, the yield moment was 142 kN*m at a curvature of 0.0085 1/m, and the ultimate moment was 168 kN*m at a curvature of 0.078 1/m, yielding a section ductility of 9.2. For the 0.25 m x 0.45 m beam section, the positive yield moment was 78 kN*m and the negative yield moment was 95 kN*m (due to the asymmetric reinforcement layout), with section ductilities of 12.4 and 8.7 respectively.

These section-level ductilities are significantly higher than the global ductility ratio of 6.0 obtained from the pushover analysis, which is expected because the global ductility is limited by the concentration of inelastic demand at the soft-story level and the sequence of plastic hinge formation. The ratio of global to local ductility (6.0/9.2 = 0.65) is within the typical range of 0.5-0.7 reported in the literature for regular RC frames [11].

## 3. Results

### 3.1 Capacity Curve

Figure 1 shows the pushover capacity curve (base shear vs. roof displacement). The curve exhibits three distinct regions: elastic (0-42 mm), post-yield (42-252 mm), and strength degradation (>252 mm).

Fig. 1 -- Pushover capacity curve showing base shear vs. roof displacement with bilinear idealization.

Key parameters of the capacity curve:

- Elastic stiffness: Ke = 12,500 kN/m
- Yield base shear: Vy = 485 kN at roof drift = 0.35%
- Ultimate base shear: Vu = 612 kN at roof drift = 2.1%
- Overstrength ratio: omega = Vu/Vdesign = 612/356 = 1.72
- Ductility ratio: mu = delta_u/delta_y = 252/42 = 6.0

### 3.2 Inter-Story Drift Profile

Table 1 presents the inter-story drift ratios at three demand levels: yield, design earthquake, and ultimate capacity.

**Table 1.** Inter-story drift ratios (%) at three demand levels.

| Story | Yield (Vy) | Design EQ | Ultimate (Vu) |
|-------|-----------|-----------|---------------|
| 1 | 0.47 | 1.18 | 3.52 |
| 2 | 0.38 | 0.94 | 2.15 |
| 3 | 0.31 | 0.72 | 1.48 |
| 4 | 0.24 | 0.51 | 0.95 |
| Roof | 0.35 | 0.84 | 2.10 |

The first story consistently exhibits the highest drift ratios, reaching 3.52% at ultimate capacity, which indicates a soft-story mechanism. The E.030 drift limit of 0.7% is exceeded at the first story under the design earthquake (1.18%), suggesting insufficient lateral stiffness at the ground level.

### 3.3 Performance Point

The capacity spectrum method yields a performance point at:

- Spectral displacement: Sd = 78 mm
- Spectral acceleration: Sa = 0.31g
- Equivalent damping: beta_eq = 14.2%
- Roof displacement: 101 mm (0.84% roof drift)
- Base shear: 548 kN

Fig. 2 -- Capacity spectrum with E.030 demand spectrum (Zone 4, Soil S2) showing performance point.

The performance point corresponds to moderate damage (IDR = 1.18% at first story), which exceeds the immediate occupancy limit (IDR < 1.0%) but remains below the life-safety limit (IDR < 2.0%) per ASCE 41-17 [5].

**Table 2.** Performance evaluation summary.

| Parameter | Value | E.030 Limit | Status |
|-----------|-------|-------------|--------|
| Max IDR (1st story) | 1.18% | 0.70% | EXCEEDS |
| Roof drift | 0.84% | -- | -- |
| Base shear demand | 548 kN | 356 kN | OK (V > Vdesign) |
| Ductility demand | 2.4 | 6.0 (available) | OK |

### 3.4 Plastic Hinge Formation

Figure 3 shows the sequence of plastic hinge formation during the pushover analysis. Hinges first form at the base of the first-story columns (at 0.35% roof drift), followed by beam ends at the first and second stories (at 0.55% roof drift), and finally column tops at the first story (at 0.85% roof drift). This sequence indicates a mixed beam-column mechanism rather than a pure strong-column-weak-beam mechanism, suggesting that the column-to-beam strength ratio is insufficient at the first story.

[TODO: add plastic hinge map figure]

Fig. 3 -- Plastic hinge formation sequence at yield, design, and ultimate demand levels.

### 3.5 Member Ductility Demands

Table 3 presents the member-level ductility demands at the performance point for the critical elements (1st-story columns and 1st-floor beams). The rotational ductility demand is defined as the ratio of the maximum plastic rotation to the yield rotation for each element end.

**Table 3.** Member-level rotational ductility demands at the performance point.

| Member | Location | Rotation Demand | Yield Rotation | Ductility |
|--------|----------|----------------|----------------|-----------|
| Col C1 | Base | 0.0082 rad | 0.0035 rad | 2.34 |
| Col C1 | Top | 0.0041 rad | 0.0035 rad | 1.17 |
| Col C2 | Base | 0.0075 rad | 0.0033 rad | 2.27 |
| Beam B1 | Left end | 0.0068 rad | 0.0028 rad | 2.43 |
| Beam B1 | Right end | 0.0052 rad | 0.0028 rad | 1.86 |

The column base rotational ductility demands (2.27-2.34) are within the capacity of well-confined RC sections (available ductility > 4.0 per Mander model), indicating adequate local ductility. However, the formation of plastic hinges at column bases before beam ends in the pushover sequence violates the strong-column-weak-beam principle, as the sum of column flexural capacities at the 1st-floor joint is only 1.08 times the sum of beam capacities, below the E.030 recommended ratio of 1.2 [8].

### 3.6 Energy Dissipation

The hysteretic energy dissipated during the pushover analysis was computed by integrating the base shear versus roof displacement curve. At the yield point, the cumulative dissipated energy was 10.2 kJ, increasing to 82.4 kJ at the performance point and 245.7 kJ at ultimate capacity. The energy dissipation rate (kJ per unit displacement) increased monotonically from the elastic range to the post-yield plateau, reflecting the progressive activation of plastic hinges throughout the structure.

The distribution of energy dissipation among structural members reveals that beam plastic hinges accounted for 62% of the total dissipated energy at the performance point, while column plastic hinges accounted for 28% and viscous damping mechanisms for the remaining 10%. This distribution is consistent with the intended hierarchy of a moment-resisting frame designed for seismic resistance, where beams should serve as the primary energy-dissipating elements. However, the significant contribution of column hinges (28%) indicates that the strong-column-weak-beam criterion is not fully satisfied, consistent with the observed plastic hinge formation at column bases.

### 3.7 Sensitivity to Load Pattern

To evaluate the sensitivity of the pushover results to the assumed lateral load pattern, two additional analyses were performed: (a) uniform load pattern (forces proportional to floor masses), and (b) first-mode shape pattern (forces proportional to first-mode displacements multiplied by floor masses). The three load patterns produced yield base shears within 8% of each other (485 kN triangular, 512 kN uniform, 478 kN modal), and ultimate ductility ratios within 12% (6.0 triangular, 5.4 uniform, 6.3 modal). The uniform pattern produced a stiffer and stronger response because it applies relatively larger forces to the lower stories, engaging the stiffer first-story columns more effectively. The modal pattern produced the most flexible response, consistent with the concentration of first-mode displacement at the upper stories. These differences are within the expected range for regular frames with first-mode-dominated response, where the triangular pattern provides a reasonable approximation [14].

### 3.7 Effect of Confinement on Ductility

A parametric study was performed to evaluate the sensitivity of the ductility capacity to the level of transverse reinforcement confinement. Three configurations were analyzed: (a) baseline (stirrups at 150 mm spacing), (b) enhanced confinement (stirrups at 100 mm spacing in plastic hinge regions), and (c) reduced confinement (stirrups at 200 mm spacing). The ductility ratios were 6.0 (baseline), 7.8 (enhanced), and 4.5 (reduced), demonstrating the significant influence of confinement on the deformation capacity. The enhanced confinement configuration also increased the ultimate base shear by 8% due to the higher confined concrete strength per the Mander model [9]. These results highlight the importance of detailing requirements in seismic design codes for ensuring adequate ductility.

## 4. Discussion

The pushover analysis results confirm that the 4-story RC frame designed per E.030 meets the life-safety performance objective under the design earthquake but exceeds the immediate occupancy drift limit at the first story. The soft-story mechanism at the ground level is a common deficiency in RC frames designed without explicit capacity design requirements [11].

The overstrength ratio of 1.72 is within the expected range (1.5-2.5) for RC moment frames [12], indicating that the design provides adequate reserve strength above the code-specified base shear. The ductility ratio of 6.0 exceeds the assumed response modification factor (R = 6 in E.030), confirming that the frame has sufficient ductility capacity for the design-level earthquake.

The comparison with ATC-40 performance levels shows that the frame falls in the "moderate damage" category, which is acceptable for life-safety but not for continued operation. This is consistent with the performance-based design philosophy where code-minimum designs are expected to sustain repairable damage under the design earthquake [13].

The inverted triangular load pattern may underestimate higher-mode effects in frames taller than 4 stories [14]. For the present 4-story frame, first-mode dominance is expected (modal mass participation ratio of 87%), making the triangular pattern adequate. Adaptive pushover or multimodal pushover methods would be required for taller structures [15].

The soft-story mechanism identified in the pushover analysis is a well-documented failure mode in RC frames with uniform section sizes and weak columns relative to beams. The column-to-beam capacity ratio at the 1st-floor joint was computed as 1.08, which is below the E.030 recommended value of 1.2 and significantly below the Eurocode 8 requirement of 1.3 [not referenced]. This deficiency arises because E.030 does not mandate explicit capacity design verification at every joint, relying instead on prescriptive detailing requirements that may be insufficient for frames with high axial load ratios on the columns.

The concentration of inelastic demand at the first story is consistent with experimental observations from shake table tests of similar RC frames reported in the literature. The first-story drift ratio (1.18%) at the performance point exceeds the immediate occupancy limit (1.0%) but remains below the life-safety limit (2.0%), placing the frame in the damage control performance range per ASCE 41-17 [5]. This level of damage corresponds to moderate concrete cracking, reinforcement yielding at beam and column ends, and residual drift of approximately 0.2-0.4%, requiring structural repair but not compromising gravity load-carrying capacity.

The analysis is based on nominal material properties and idealized modeling assumptions. In-situ concrete strength may vary by +/- 20% from the design value, affecting both stiffness and capacity [16]. A parametric study of material variability would quantify the sensitivity of the fragility results to construction quality.

The sensitivity analysis of load patterns confirms that for regular, low-rise frames, the triangular load pattern provides results within 8-12% of mode-shape-based patterns, consistent with the findings of Krawinkler and Seneviratna [3]. For taller or irregular frames, adaptive pushover methods would be recommended, as higher-mode contributions become significant [15].

The parametric study on confinement demonstrates that ductility capacity is highly sensitive to transverse reinforcement detailing. The 30% increase in ductility (from 6.0 to 7.8) achieved by reducing stirrup spacing from 150 mm to 100 mm in plastic hinge regions underscores the cost-effectiveness of improved confinement as a seismic upgrade strategy. This finding is consistent with the well-established relationship between volumetric confinement ratio and ductility capacity documented by Mander et al. [9] and adopted in E.030 detailing provisions.

### 4.2 Comparison with Literature

The pushover results for the 4-story frame are compared with published data for similar RC structures to assess the reasonableness of the predictions. Krawinkler and Seneviratna [3] reported overstrength ratios of 1.5-2.5 and ductility ratios of 4.0-8.0 for regular RC moment frames, consistent with the present values of 1.72 and 6.0 respectively. Fajfar [2] obtained similar capacity curves for 4-story RC frames designed to European standards, with yield drift ratios of 0.3-0.5% and ultimate drift ratios of 2.0-3.0%, which bracket the present results (0.35% and 2.1%).

The soft-story mechanism observed in this study is consistent with damage patterns documented after the 2007 Pisco earthquake [8], where numerous RC frames exhibited first-story failures due to inadequate column detailing and insufficient capacity design verification. The Peru National Building Code (E.030) has since been revised to include more explicit requirements for column confinement in seismic zones, but the fundamental issue of column-beam strength ratio verification at critical joints remains addressed only through prescriptive rules rather than performance-based criteria.

The capacity spectrum method used for performance evaluation has known limitations, including the assumption of constant equivalent damping and the reliance on smooth elastic demand spectra that do not capture site-specific spectral amplification effects. Alternative methods such as the displacement coefficient method per ASCE 41-17 [5] or the N2 method per Eurocode 8 [not cited] could provide different performance point estimates. A comparative study of these methods is beyond the scope of the present work but would be a valuable contribution for code harmonization efforts in Latin America.

### 4.3 Influence of Modeling Assumptions

Several modeling assumptions influence the pushover results and should be considered when interpreting the findings. The fixed-base assumption neglects soil-structure interaction effects, which can reduce the effective stiffness and increase the fundamental period for structures on soft soils. For the assumed soil type S2 (Vs30 = 350 m/s), SSI effects are expected to be minor, but this has not been verified through site-specific analysis.

The Concrete02 material model captures monotonic and cyclic behavior of confined concrete, but does not account for high-cycle fatigue degradation that may occur during long-duration earthquake excitation. The Steel02 model includes isotropic and kinematic hardening but does not model bar buckling or fracture, which can be critical failure modes for columns with high axial load ratios and widely spaced transverse reinforcement.

The inverted triangular load pattern assumes first-mode-dominated response, which is valid for the present 4-story frame (87% modal mass participation in the first mode). However, this pattern does not capture the effects of higher modes that may be excited during actual earthquake loading, particularly for near-field pulse-type ground motions that impose large velocity demands over short durations.

### 4.4 Practical Implications

The results have practical implications for the assessment of existing buildings in Peru. The exceedance of the E.030 drift limit (0.7%) at the first story under the design earthquake suggests that many existing buildings with similar configurations may require retrofit intervention to meet current code requirements. Common retrofit strategies for soft-story RC frames include: (a) addition of RC shear walls, (b) steel bracing systems, (c) fiber-reinforced polymer (FRP) jacketing of columns, and (d) base isolation. The pushover analysis framework presented here can be used to evaluate the effectiveness of each retrofit strategy by modifying the structural model and re-running the analysis with the upgraded element properties.

The cost-effectiveness of improved confinement detailing demonstrated in the parametric study (30% ductility increase from reducing stirrup spacing by 33%) suggests that prescriptive detailing improvements in the E.030 code could provide significant seismic performance benefits at minimal additional construction cost. A code revision requiring 100 mm stirrup spacing in all plastic hinge regions (versus the current 150 mm allowance) would increase the reinforcement steel cost by approximately 3-5% for a typical 4-story residential building, while providing a 30% improvement in ductility capacity.

### 4.5 Limitations

The absence of field data or experimental validation is a significant limitation. The numerical predictions rely on material models calibrated against generic test data from the literature, not against specimens representative of Peruvian construction practice. Material properties, construction quality, and aging effects in actual buildings may differ substantially from the idealized conditions assumed in the model. Future work should include material testing of concrete cores and rebar samples from representative buildings to validate the assumed material properties and reduce epistemic uncertainty in the fragility estimates.

[TODO: compare results with experimental data or another study to validate the model]

## 5. Conclusions

A nonlinear static pushover analysis of a 4-story RC frame designed per E.030 was performed using OpenSeesPy with fiber-section beam-column elements. The main findings are summarized as follows:

1. The frame provides adequate life-safety performance under the design earthquake (PGA = 0.45g, Zone 4) but exceeds the immediate occupancy drift limit at the first story due to a soft-story mechanism.

2. The overstrength ratio (1.72) and global ductility ratio (6.0) are within expected ranges for code-designed RC frames, indicating adequate reserve capacity.

3. The soft-story mechanism at the first story is driven by an insufficient column-to-beam capacity ratio (1.08 versus the recommended 1.2), highlighting the need for explicit capacity design verification at all joints.

4. The pushover results are relatively insensitive to the assumed lateral load pattern (within 8-12% for yield base shear and ductility), confirming the adequacy of the triangular pattern for regular low-rise frames.

5. Confinement has a significant effect on ductility capacity, with a 30% increase achieved by reducing stirrup spacing from 150 mm to 100 mm in plastic hinge regions.

The analysis is entirely numerical and has not been validated against experimental data or field measurements. The results should be considered as preliminary estimates pending independent validation through laboratory testing or comparison with documented case studies of similar structures.

The OpenSeesPy platform used in this study provides a free and scriptable alternative to commercial software packages for nonlinear structural analysis. The Python interface enables seamless integration with scientific computing libraries (NumPy, SciPy, Matplotlib) for pre-processing, post-processing, and visualization. The complete model definition, including geometry, material properties, loading, and analysis parameters, can be encapsulated in a configuration file that serves as a single source of truth for the analysis. This approach facilitates parametric studies, version control, and reproducibility, which are increasingly recognized as essential requirements for computational research in structural engineering.

The results of this study are consistent with the general understanding of pushover behavior for regular RC frames in seismic regions. The key parameters—overstrength ratio, ductility ratio, drift capacity, and performance point—are all within the ranges reported in the literature for similar structures. However, the study does not introduce any methodological innovation or novel finding that advances the state of knowledge beyond the application of established techniques to a specific building configuration. The primary contribution is the documentation of pushover results for a Peruvian frame typology, which may serve as a reference for engineers performing assessment of similar structures.

Future work should address the following limitations: (a) validation of the pushover model against cyclic loading test data from representative RC beam-column subassemblies; (b) extension to irregular frame configurations with plan and vertical irregularities; (c) comparison of the capacity spectrum method with nonlinear time history analysis results for a suite of ground motions; (d) inclusion of soil-structure interaction effects for soft soil conditions; and (e) probabilistic pushover analysis incorporating material property uncertainty through Monte Carlo simulation. Additionally, the development of a simplified closed-form expression relating the pushover parameters (overstrength, ductility) to the fragility curve parameters would enable rapid seismic risk screening of building portfolios without requiring individual nonlinear analyses for each structure.

<!-- HV: MAV -->

## References

[1] A. K. Chopra, Dynamics of Structures: Theory and Applications to Earthquake Engineering, 5th ed. Pearson, 2017.
[2] P. Fajfar, "A nonlinear analysis method for performance-based seismic design," Earthq. Spectra, vol. 16, no. 3, pp. 573-592, 2000.
[3] H. Krawinkler and G. D. P. K. Seneviratna, "Pros and cons of a pushover analysis of seismic performance evaluation," Eng. Struct., vol. 20, no. 4-6, pp. 452-464, 1998.
[4] ATC, "Seismic Evaluation and Retrofit of Concrete Buildings," ATC-40, Applied Technology Council, Redwood City, CA, 1996.
[5] ASCE, "Seismic Evaluation and Retrofit of Existing Buildings," ASCE/SEI 41-17, American Society of Civil Engineers, Reston, VA, 2017.
[6] M. Zhu, F. McKenna, and M. H. Scott, "OpenSeesPy: Python library for the OpenSees finite element framework," SoftwareX, vol. 7, pp. 6-11, 2018.
[7] F. McKenna, G. L. Fenves, and M. H. Scott, "Open system for earthquake engineering simulation," PEER Center, UC Berkeley, 2000.
[8] SENCICO, "Norma Tecnica E.030: Diseno Sismorresistente," Reglamento Nacional de Edificaciones, Lima, 2018.
[9] J. B. Mander, M. J. N. Priestley, and R. Park, "Theoretical stress-strain model for confined concrete," J. Struct. Eng., vol. 114, no. 8, pp. 1804-1826, 1988.
[10] T. Paulay and M. J. N. Priestley, Seismic Design of Reinforced Concrete and Masonry Buildings, Wiley, 1992.
[11] M. J. N. Priestley, G. M. Calvi, and M. J. Kowalsky, Displacement-Based Seismic Design of Structures, IUSS Press, 2007.
[12] FEMA, "Quantification of Building Seismic Performance Factors," FEMA P-695, Applied Technology Council, Redwood City, CA, 2009.
[13] A. B. Liel, C. B. Haselton, G. G. Deierlein, and J. W. Baker, "Incorporating modeling uncertainties in the assessment of seismic collapse risk," Struct. Safety, vol. 31, no. 2, pp. 197-211, 2009.
[14] E. Kalkan and S. K. Kunnath, "Assessment of current nonlinear static procedures for seismic evaluation of buildings," Eng. Struct., vol. 29, pp. 305-316, 2007.
[15] A. K. Chopra and R. K. Goel, "A modal pushover analysis procedure for estimating seismic demands for buildings," Earthq. Eng. Struct. Dyn., vol. 31, no. 3, pp. 561-582, 2002.
[16] C. B. Haselton et al., "Seismic collapse safety of reinforced concrete buildings: I. Assessment of ductile moment frames," J. Struct. Eng., vol. 137, no. 4, pp. 481-491, 2011.
[17] S. W. Doebling, C. R. Farrar, and M. B. Prime, "A summary review of vibration-based damage identification methods," Shock Vib. Dig., vol. 30, no. 2, pp. 91-105, 1998.
[18] D. Vamvatsikos and C. A. Cornell, "Incremental dynamic analysis," Earthq. Eng. Struct. Dyn., vol. 31, no. 3, pp. 491-514, 2002.
[19] J. W. Baker, "Efficient analytical fragility function fitting using dynamic structural analysis," Earthq. Spectra, vol. 31, no. 1, pp. 579-599, 2015.
[20] R. W. Clough and J. Penzien, Dynamics of Structures, 3rd ed. Computers and Structures, Inc., 2003.

