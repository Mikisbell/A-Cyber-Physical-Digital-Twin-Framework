# Skill: CFD Domain (Water)

## Trigger
Load when: domain is "water", working with FEniCSx, Navier-Stokes, hydraulics, dams, or pipe flow.

## Domain Context

The water domain uses FEniCSx as its solver backend for:
- Incompressible Navier-Stokes (pipe flow, open channels)
- Free surface flow (dam breaks, spillways)
- Fluid-structure interaction (submerged structures, piers)
- Hydraulic SHM (pressure monitoring, flow anomalies)

## SSOT Parameters
All water domain params live in `config/params.yaml` under `fluid:`:
```yaml
fluid:
  density_rho: null      # kg/m3
  viscosity_mu: null     # Pa·s
  velocity_inlet: null   # m/s
  reynolds_number: null  # dimensionless
  mesh_refinement: null  # levels
  time_step_dt: null     # seconds
  turbulence_model: null # laminar|k-epsilon|LES
  boundary_type: null    # no-slip|free-slip|inlet|outlet
  domain_length: null    # meters
  domain_height: null    # meters
```

## FEniCSx Patterns

### Mesh Generation
```python
from dolfinx import mesh
domain = mesh.create_rectangle(
    MPI.COMM_WORLD,
    [np.array([0, 0]), np.array([L, H])],
    [nx, ny],
    cell_type=mesh.CellType.triangle
)
```

### Weak Form (Navier-Stokes)
```python
# Variational form: find (u, p) such that
# (u_t, v) + (u·∇u, v) + ν(∇u, ∇v) - (p, ∇·v) = (f, v)
# (∇·u, q) = 0
```

### Convergence Checks
- Mesh convergence study: run at 3 refinement levels, check < 2% change
- CFL condition: dt < dx / u_max
- Residual norm < 1e-6 per time step

## Paper Sections (Water Domain)
When writing papers for water domain:
- **Methodology**: Describe governing equations (NS), discretization (FEM), stabilization
- **Results**: Velocity profiles, pressure contours, drag/lift coefficients
- **Validation**: Compare against analytical solutions (Poiseuille, Couette) or experimental data

## Key References (auto-loaded from bibliography_engine)
Categories: `cfd`, `hydraulics`
- Logg et al. 2012 (FEniCS book)
- Alnaes et al. 2015 (UFL)
- Scroggs et al. 2022 (Basix)
- John 2016 (FEM for NS)
- Chanson 2004 (Hydraulics of open channel flow)

## Verification Protocol
The Verifier must check:
1. Mass conservation: ∫(∇·u)dΩ ≈ 0
2. Energy balance: kinetic + potential + dissipation = input
3. Mesh independence (3-level convergence study)
4. CFL number < 1 for explicit schemes
