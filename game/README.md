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
