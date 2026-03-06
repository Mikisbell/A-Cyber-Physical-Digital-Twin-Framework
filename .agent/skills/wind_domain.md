# Skill: Wind Engineering Domain (Air)

## Trigger
Load when: domain is "air", working with SU2/FEniCSx for wind, aerodynamics, or ventilation.

## Domain Context

The air domain uses FEniCSx or SU2 as solver for:
- Wind load analysis on structures (ASCE 7, Eurocode 1)
- Aerodynamic coefficients (Cp, Cd, Cl)
- Vortex-induced vibration (VIV)
- Natural ventilation and thermal comfort
- Wind tunnel validation (CFD vs experimental)

## SSOT Parameters
All air domain params live in `config/params.yaml` under `air:`:
```yaml
air:
  wind_speed: null         # m/s (reference at 10m height)
  air_density: null        # kg/m3 (typically 1.225)
  kinematic_viscosity: null # m2/s
  turbulence_intensity: null # %
  roughness_length: null   # m (terrain category)
  reference_height: null   # m
  exposure_category: null  # A|B|C|D (ASCE 7)
  gust_factor: null        # dimensionless
  mesh_type: null          # structured|unstructured|hybrid
  solver: null             # fenics|su2
  angle_of_attack: null    # degrees
  domain_radius: null      # multiples of characteristic length
```

## Wind Profile (Atmospheric Boundary Layer)
```python
# Power law profile
U(z) = U_ref * (z / z_ref) ** alpha

# Log law profile
U(z) = (u_star / kappa) * ln(z / z_0)
```

Alpha values by terrain:
| Terrain | alpha | z_0 (m) |
|---------|-------|---------|
| Open water | 0.10 | 0.003 |
| Open terrain | 0.14 | 0.03 |
| Suburban | 0.22 | 0.3 |
| Urban center | 0.33 | 1.0 |

## SU2 Integration
```bash
# Run SU2 CFD solver
SU2_CFD config.cfg
# Post-process
SU2_SOL config.cfg
```

Key config parameters:
- `SOLVER= RANS` or `SOLVER= EULER`
- `TURB_MODEL= SA` (Spalart-Allmaras) or `SST` (Menter k-omega SST)
- `MESH_FILENAME= mesh.su2`

## Paper Sections (Air Domain)
- **Methodology**: ABL profile, turbulence model selection, mesh strategy
- **Results**: Cp distribution, drag coefficients, flow visualization
- **Discussion**: Compare CFD vs wind code provisions (ASCE 7 / Eurocode 1)

## Key References
Categories: `cfd`, `wind`
- Simiu & Yeo 2019 (Wind Effects on Structures)
- Kareem et al. 2020 (Aeroelasticity)
- Blocken 2015 (CFD for urban physics)
- SU2 Team 2016 (Stanford solver)

## Verification Protocol
1. Pressure coefficient validation: Cp vs wind tunnel data
2. Grid convergence index (GCI): 3-mesh Richardson extrapolation
3. y+ check: first cell height appropriate for wall treatment
4. Strouhal number (if VIV): compare vs empirical St ≈ 0.2
