# StarGen — 4X + 6DOF RSVP Simulator

A minimal, compilable Java skeleton for a Descent-style 6DOF space shooter fused with Stars!-style tech/economy, instrumented with RSVP fields (Φ, 𝒗, S, λ).

## Build & Run (Gradle)
```bash
./gradlew run
```

## Packages
- `com.stargen.math` — core math
- `com.stargen.engine` — loop + integration
- `com.stargen.engine.simulation` — RSVP fields and stability
- `com.stargen.entities` — ships & projectiles
- `com.stargen.entities.ai` — simple AI controller
- `com.stargen.controls` — input mapping
- `com.stargen.graphics` — placeholder renderer + HUD
- `com.stargen.research` — tech tree
- `com.stargen.world` — galaxy/regions with Φ,S fields
- `com.stargen.missions` — tactical operations affecting RSVP

## RSVP Coupling
- WorldState evolves Φ,S,λ each tick; R = Φ - λS.
- High entropy (S) injects handling instability in PlayerShip, and AI aim noise.
- Tech unlocks modify Φ,S,λ to demo takeoff-rate management.


---

## Code Generator (StarGen.js)
Node-based generator for emitting Java sources.

### Commands
```bash
npm run gen:all       # emit WorldState, Technology, TechTree, and patch GameLoop
npm run gen:world     # only WorldState
npm run gen:research  # Technology + TechTree
npm run gen:patch     # ensure GameLoop has fields & tick hooks
```

### Data-driven techs
See `research.techs.json` (example). You can extend `StarGen.js` to read this file and generate initializers.


### Mission DSL
Simple key=value format without external JSON deps:
```ini
type=STABILIZE_NODE
node=0
duration=45
effect=entropy:-0.02
```
File example at `missions/sample.mis`. Parsed by `MissionDSL` and run by `ScriptMission`.

### Collision & Health
- `Entity` now has `health`, `radius`, `active`, and `takeDamage(d)`.
- `CollisionManager` resolves projectile→actor hits (naive sphere checks).

### Renderer backends
- `graphics/backends/LwjglRendererShell` and `JmeRendererShell` compile as placeholders; wire real libs later.


### Tech schema & UI
- Schema: `research.techs.schema.json`
- Data: `research.techs.json` (tiers, branches, prereqs)
- UI: `TechUI` prints menu every ~3s; press 1–9 (via `InputHandler.setKeyState`) to unlock by index.

### AI loadouts & states
- `AIController` now supports `CHASE`, `ATTACK`, `EVADE` and fires projectiles on cooldown.

### Voxel tunnel generator
- `world/TunnelGenerator` produces a Descent-like tunnel network in a `TunnelLevel` volume.

### Renderer backend interface
- `graphics/RendererBackend` and default `StubRenderer` for dependency-free runs.
- LWJGL/JME shells remain in `graphics/backends/` to wire later.

### Save/Load
- `io/WorldSerializer.save(path, world, techTree)` writes a JSON snapshot.


### v5 Additions
- `Main.java` (entry point delegating to `GameLoop`)
- `TechLogic` (prereqs/tier gating via `research.techs.json`)
- `MissionFactory` (script/procedural missions)
- `WorldLoader` (load snapshot back)
- `NavMesh` (voxel graph + BFS)
- `ConfigLoader` + `config/game.properties`
- Patched `WorldState` to include `addPhi` / `addEntropy`


### v6 Additions
- `HUDRenderer` (telemetry), `LWJGLRenderer` (compile-safe stub backend).
- `AIPathFollower` uses `NavMesh` BFS to move node-to-node.
- `TechTree.unlock()` now enforces prereqs/tier via `TechLogic` and applies dΦ/dS/dλ.
- `build.gradle` includes Jackson and sets `com.stargen.Main` as the entry point.


### v7 Demo & Tests
- Demo scene in `GameLoop`: spawns `AIPathFollower` and builds a simple `NavMesh` over an empty voxel grid; HUD prints Φ, S, λ, R each second.
- JUnit tests: `WorldStateTest`, `TechLogicTest`.
- Run tests: `./gradlew test`.


### v9: In-window Tech Overlay + RSVP-Coupled Renderer + ASCII Levels
- **TechScreen (overlay)**: Press `T` to open in LWJGL window; `1..9` to attempt unlocks (prereqs enforced).
- **RSVP visual coupling**: Φ → point size (zoom), S → background jitter, λ → hue shift, R → brightness.
- **LevelLoader**: Reads ASCII maps from `assets/levels/*.txt` into `TunnelLevel` and builds a NavMesh.
- **Assets**: `level1.txt`, `level2.txt` included.
Run the LWJGL demo: `./gradlew run -Drenderer=lwjgl`
