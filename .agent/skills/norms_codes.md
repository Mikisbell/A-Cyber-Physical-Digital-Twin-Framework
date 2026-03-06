# Skill: Engineering Norms and Design Codes

## Trigger
Load when: referencing design codes, seismic norms, load combinations, or code-based verification.

## Active Codes by Domain

### Structural (Seismic)
| Code | Scope | Key Parameters |
|------|-------|----------------|
| **E.030 (Peru)** | Seismic design | Z, U, S, C, R factors |
| **Eurocode 8** | Seismic design | ag, S, TB, TC, TD, q |
| **ASCE 7-22** | Loads | SDS, SD1, Fa, Fv, R, Cd |
| **ACI 318-19** | Concrete | fc', fy, phi factors |
| **AISC 360-22** | Steel | Fy, Fu, phi, Omega |

### Water (Hydraulics)
| Code | Scope |
|------|-------|
| **ACI 350** | Environmental engineering concrete |
| **FEMA P-93** | Dam safety |
| **USACE EM 1110** | Hydraulic structures |

### Air (Wind)
| Code | Scope |
|------|-------|
| **ASCE 7-22 Ch.26-31** | Wind loads |
| **Eurocode 1 Part 1-4** | Wind actions |
| **AS/NZS 1170.2** | Wind actions (Australasia) |

## E.030 Quick Reference (Peru Seismic Code)

### Seismic Zonation
| Zone | Z factor |
|------|----------|
| Z4 | 0.45 |
| Z3 | 0.35 |
| Z2 | 0.25 |
| Z1 | 0.10 |

### Site Amplification
| Soil | S | TP (s) | TL (s) |
|------|---|--------|--------|
| S0 (hard rock) | 0.80 | 0.30 | 3.0 |
| S1 (rock) | 1.00 | 0.40 | 2.5 |
| S2 (firm soil) | 1.05 | 0.60 | 2.0 |
| S3 (soft soil) | 1.10 | 1.00 | 1.6 |

### Spectral Acceleration
```
C = 2.5 * (TP/T)        for T < TL
C = 2.5 * (TP*TL/T^2)   for T >= TL
Sa = Z * U * C * S / R
```

## Eurocode 8 Quick Reference

### Damping Correction (eta)
```
eta = sqrt(10 / (5 + xi))   where xi = damping ratio in %
```
For xi = 5%: eta = 1.0 (reference)
For xi = 2%: eta = 1.195

### Design Spectrum
```
0 <= T <= TB:    Sd = ag*S*[2/3 + T/TB*(2.5/q - 2/3)]
TB <= T <= TC:   Sd = ag*S*2.5/q
TC <= T <= TD:   Sd = ag*S*2.5/q*(TC/T)
TD <= T:         Sd = ag*S*2.5/q*(TC*TD/T^2)
```

## Load Combinations (ASCE 7)
```
1.4D
1.2D + 1.6L + 0.5(Lr or S or R)
1.2D + 1.6(Lr or S or R) + (L or 0.5W)
1.2D + 1.0W + L + 0.5(Lr or S or R)
1.2D + 1.0E + L + 0.2S
0.9D + 1.0W
0.9D + 1.0E
```

## Verification Checklist
When the Verifier checks code-based results:
1. Identify which code applies (from domain + location)
2. Verify load factors match the code edition
3. Check capacity reduction factors (phi) are correct
4. Verify drift limits: structural (0.7-2.5% depending on code)
5. Check period bounds: T_code vs T_model (must be within 20%)
6. Site amplification: soil type matches field conditions
