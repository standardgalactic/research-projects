# RSVP Lab Package

A modular simulation environment for the RSVP (Relativistic Scalar-Vector Plenum)
field framework, including TARTAN recursive tiling, CLIO constraint repair, semantic
attractor dynamics, topological metrics, and cosmological extensions.

## Package structure

```
notebooks/
    rsvp_field_laboratory.ipynb   17-cell experimental notebook (full)

operators/
    rsvp.py        Core field dynamics — Φ, v, S, R; evolve(); fractional Laplacian
    clio.py        Repair operators — standard / regulatory / sheaf / identity / economic
    semantic.py    Attractor fields — Coulomb potential, basin maps, observer projections
    topology.py    Topological metrics — gluing obstruction, TARTAN, PCA, persistence
    cosmology.py   Expansion — Hubble drag, coupled manifolds, extractive economy

data/            Save field snapshots here (numpy .npy / .npz)
results/         Save figures and animations here
```

## Suggested workflow

1. Open `notebooks/rsvp_field_laboratory.ipynb` in Jupyter.
2. Run Cell 1 (imports) and Cell 2 (baseline simulation) to populate history arrays.
3. Run individual experiment cells in any order — each resets its own fields.
4. Use `field_metrics()` from `operators/rsvp.py` to log scalar observables.
5. Save snapshots: `np.save('data/phi_final.npy', phi)`.

## Operator quick-reference

### rsvp.py
| Function                | Purpose                                      |
|-------------------------|----------------------------------------------|
| `init_fields(H,W)`      | Initialise Φ, vx, vy, S, R                  |
| `evolve(...)`           | Standard RSVP step (accepts clio_fn hook)    |
| `evolve_fractional(...)`| Step with (−∇²)^α spectral diffusion         |
| `inject_kink(...)`      | Place a tanh soliton on the scalar field     |
| `admissibility(...)`    | Float mask of trajectory-admissible cells    |
| `field_metrics(...)`    | Dict of scalar summary statistics            |
| `coarse_grain(...)`     | Tile-mean coarse-graining map F(Φ)           |

### clio.py
| Function / factory      | Purpose                                      |
|-------------------------|----------------------------------------------|
| `clio_standard(...)`    | Gradient-tension smoothing repair            |
| `clio_regulatory(...)`  | Seed-biased anisotropic repair               |
| `clio_sheaf(...)`       | Patch-gluing obstruction repair              |
| `clio_identity(...)`    | Self-consistency (coarse-grain) repair       |
| `clio_economic(...)`    | Capital-concentration regulator              |
| `get_clio(name, **kw)`  | Factory returning a pre-bound callable       |

### semantic.py
| Class / Function          | Purpose                                    |
|---------------------------|--------------------------------------------|
| `SemanticField(H,W,...)`  | Manages token positions, charges, basins   |
| `semantic_potential(...)` | Coulomb V(x,y) = Σ qᵢ/(rᵢ+ε)             |
| `observer_projection(...)` | Line-of-sight projection of any field     |
| `anisotropy_index(...)`   | σ/μ of projected entropies across observers|
| `evolve_semantic(...)`    | RSVP step with semantic forcing            |

### topology.py
| Function                 | Purpose                                     |
|--------------------------|---------------------------------------------|
| `gluing_obstruction(...)`| Global sheaf cocycle error Ω                |
| `local_gluing_map(...)`  | Spatial obstruction grid                    |
| `connected_components(…)`| Level-set component count                   |
| `euler_characteristic(…)`| Discrete χ of super-level set              |
| `persistence_diagram(…)` | Crude 0-D sublevel persistence              |
| `tartan_tiles(...)`      | Single-scale tile stats (mean/var/skew)     |
| `tartan_hierarchy(...)`  | Multi-scale recursive tiling                |
| `pca_embedding(...)`     | Low-D PCA trajectory of field snapshots     |
| `synchrony(f1, f2)`      | Pearson correlation between two fields      |
| `gini(field)`            | Gini coefficient of a non-negative field    |
| `structure_function(...)`| Second-order structure function D(r)        |

### cosmology.py
| Class / Function            | Purpose                                  |
|-----------------------------|------------------------------------------|
| `hubble_expand(a, H0, dt)`  | Advance scale factor a(t)                |
| `evolve_cosmological(...)`  | RSVP step on expanding background        |
| `CosmologicalHistory`       | Records a(t), σ(Φ), entropy mean         |
| `evolve_coupled(...)`       | Two-manifold step with ε coupling        |
| `EconomicField`             | Capital/Labour/Precarity system + Gini   |
| `double_well_force(φ, μ)`  | Soliton-supporting −dV/dΦ force          |

## Experiments in the notebook

| Cell | Experiment                          | Key observable                     |
|------|-------------------------------------|------------------------------------|
| 2    | Baseline 1000-step RSVP run         | history arrays, metrics_log        |
| 3    | Tri-panel animation                 | Φ, S, ω animated                  |
| 4    | Phase metrics + admissibility       | energy curves, admissible fraction |
| 5    | Sheaf gluing obstruction            | Ω(t), spatial obstruction map      |
| 6    | TARTAN hierarchy + structure fn     | tile histograms, D(r) scaling      |
| 7    | Level-set topology                  | components, χ, persistence pairs   |
| 8    | Semantic attractors                 | basin map, inter-basin flux        |
| 9    | Observer projections                | anisotropy index                   |
| 10   | Fractional Laplacian scan           | α ∈ {0.5,1.0,1.5} comparison       |
| 11   | Soliton kink collision              | kink early/collision/late          |
| 12   | Hubble expansion                    | a(t), σ(Φ), horizon crossing       |
| 13   | Coupled manifolds                   | synchrony C(t)                     |
| 14   | Extractive economy                  | Gini(K), ⟨L⟩                      |
| 15   | Recursive identity constraint       | identity gap ‖Φ−F(Φ)‖²           |
| 16   | PCA state-space embedding           | 2-D trajectory, effective dim      |
| 17   | Composite dashboard                 | all observables in one figure      |

## Dependencies

```
numpy scipy matplotlib IPython
```

No GPU required.  All simulations run on CPU in reasonable time on a modern laptop.
