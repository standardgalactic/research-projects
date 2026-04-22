# Flash-Reluctance Engine — Blender bpy Scripts
## Four-Script Pipeline

### Execution Order

Run these in sequence from Blender's **Scripting** workspace
(Text Editor → Open → select file → Run Script):

```
fr_01_rotor_geometry.py     ← Run first
fr_02_thermal_system.py     ← Run second  (adds to same collection)
fr_03_animation.py          ← Run third   (keyframes the assembly)
fr_04_analysis.py           ← Run anytime (analysis only, no bpy needed)
```

---

### Script 01 — Rotor Geometry

Builds the rotating assembly:

- **FR_Flywheel** — main disc, hub hole booleaned out
- **FR_Vane_00…NN** — tapered radial vanes (N_CHAMBERS total), angled
  per chamber spacing, slightly wider at root than tip
- **FR_Hub** — central hub with keyway slot
- **FR_Shaft** + **FR_ShaftCollar** — output shaft stub
- **FR_StatorCoil_00…NN** — coil cylinders on outer ring (blue emission)
- **FR_HousingRing** / **FR_HousingRing_Top** — structural torus rings

All objects land in the **FR_Engine** collection.
Materials are: Steel (rotor), orange-tinted Inconel (vanes), blue-emissive (coils).

Key parameters at top of file:
```python
R_ROTOR         = 0.15   # m — rotor tip radius
N_CHAMBERS      = 6
PULSE_WIDTH_DEG = 40.0   # ° — chamber arc width
```

---

### Script 02 — Thermal System

Adds the heat/fluid architecture:

- **FR_BurnerCore** + **FR_BurnerInnerGlow** — central heat manifold
  (orange emission, R = R_HUB * 0.85)
- **FR_HotWall_00…NN** — arc-section liners at mid-radius, one per chamber,
  spanning exactly PULSE_WIDTH_DEG of arc
- **FR_Nozzle_00…NN** + **FR_NozzleTip_00…NN** — injection tubes aimed
  tangentially with 15° inward rake toward hot wall
- **FR_ColdManifold** — condenser torus ring, axially offset below the disc
- **FR_CoolantInlet** / **FR_CoolantOutlet** — pipe stubs with flanges
- **FR_Exhaust_00…NN** — slim slots at end of each expansion arc

The geometry directly encodes the thermodynamic logic:
hot walls face the rotor center; nozzles inject inward-tangentially;
cold ring is spatially separated (below and outside).

---

### Script 03 — Physics-Driven Animation

Runs the same Euler integrator as the HTML simulator, then applies results
to Blender as keyframes:

**Rotor rotation** — FR_Flywheel, FR_Hub, all vanes, shaft are keyframed
with the physics-correct cumulative angle. Interpolation is set to LINEAR
(not Bezier) so angular acceleration is physically accurate.

**Stator coil emission** — each coil is keyframed independently:
- Orange glow when that chamber is in thermal expansion phase
- Blue glow when EM assist pulse is active
- White briefly if both overlap
- Dim (strength 0.2) when idle

**Nozzle flash** — injection peak lights up each nozzle at flash moment.

**CSV log** written to `/tmp/fr_torque_log.csv` — columns:
`frame, theta, omega, tau_th, tau_em, tau_fr, tau_net`

Adjust at top of script:
```python
T_WALL       = 400.0   # °C
TAU_EM_PEAK  = 12.0    # N·m  (set 0 to disable EM)
SIM_DURATION = 4.0     # s
FPS          = 24
```

Press **Space** in Blender viewport to play. Scrub timeline to inspect
individual chamber activation frames.

---

### Script 04 — Analysis & Parameter Sweep

Pure physics — no bpy dependency. Can run inside or outside Blender.

Produces four matplotlib figures saved to `/tmp/`:

| File | Content |
|------|---------|
| `fr_analysis_torque.png` | Torque waveform over one revolution |
| `fr_analysis_omega.png` | Speed ramp-up for T=250/400/600°C |
| `fr_analysis_phase_sweep.png` | Optimal EM phase offset search |
| `fr_analysis_chamber_sweep.png` | Torque + ripple vs N_chambers |

Also prints a numeric summary to console: P_peak, average torques,
ripple percentage, operating point table, phase sweep table.

View plots from Blender: **Image Editor → Open → /tmp/fr_analysis_*.png**

If matplotlib is not installed in Blender's Python:
```python
import subprocess
subprocess.run([bpy.app.binary_path_python, '-m', 'pip', 'install', 'matplotlib'])
```
Then restart Blender and re-run script 04.

---

### Parameter Synchronization

All four scripts share the same top-of-file parameter block.
When you change a value, update it in all scripts before re-running.
The canonical parameters are:

```python
R_ROTOR         = 0.15      # m
R_HUB           = 0.04      # m
N_CHAMBERS      = 6
PULSE_WIDTH_DEG = 40.0      # °
FLYWHEEL_THICK  = 0.025     # m
VANE_HEIGHT     = 0.040     # m
T_WALL          = 400.0     # °C (thermal scripts + animation)
M_INJ           = 0.002     # kg/pulse
I_ROTOR         = 0.80      # kg·m²
K_DRAG          = 0.04
TAU_EM_PEAK     = 12.0      # N·m
EM_PHASE_DEG    = 15.0      # °
```

These map directly to the HTML simulator sliders.
The geometry (scripts 01–02) follows R_ROTOR, N_CHAMBERS, PULSE_WIDTH_DEG.
The dynamics (scripts 03–04) follow the physics parameters.

---

### Recommended Workflow

1. Set parameters in script 01, run → inspect geometry in viewport
2. Run script 02 → check nozzle alignment with hot-wall arcs
3. Run script 04 → read the phase sweep, find optimal EM_PHASE_DEG
4. Update EM_PHASE_DEG in script 03, run → play animation
5. Scrub to a frame where one chamber is firing, inspect coil colors
6. Open `/tmp/fr_torque_log.csv` to verify frame-level torque values
7. Render from FR_Cam with Cycles (enable Bloom for coil glow)

---

### Blender Version Notes

Scripts tested on Blender 3.6 LTS and 4.x.
Boolean modifiers (hub hole, keyway) use the default FAST solver.
If geometry looks incorrect, switch to EXACT in the modifier panel.
Torus objects use `bpy.ops.mesh.primitive_torus_add` which requires
the viewport context — run from Scripting workspace, not background mode.
