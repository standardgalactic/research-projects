#!/usr/bin/env sh
set -e

echo "Initializing Stars! Field Explorer project..."

# ----------------------------
# Directory structure
# ----------------------------
mkdir -p \
  core \
  world \
  gameplay \
  systems \
  ui \
  data

# ----------------------------
# index.html
# ----------------------------
cat > index.html <<'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Stars! – Field Explorer</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <style>
    body { margin: 0; overflow: hidden; background: black; color: #0f0; }
    canvas { display: block; }
  </style>
</head>
<body>
  <script type="module" src="./main.js"></script>
</body>
</html>
EOF

# ----------------------------
# main.js
# ----------------------------
cat > main.js <<'EOF'
import { initRenderer, renderLoop } from "./core/renderer.js";
import { initInput } from "./core/input.js";
import { Universe } from "./world/universe.js";
import { HUD } from "./ui/hud.js";
import { CLAIM_ADJUSTER } from "./systems/traits.js";

window.__race = CLAIM_ADJUSTER;

const universe = new Universe();
const hud = new HUD(universe);

initRenderer(universe, hud);
initInput(universe);

renderLoop();
EOF

# ----------------------------
# core/renderer.js
# ----------------------------
cat > core/renderer.js <<'EOF'
import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.160/build/three.module.js";
import { updateTime } from "./time.js";

let scene, camera, renderer;
let universe, hud;
let last = performance.now();

export function initRenderer(u, h) {
  universe = u;
  hud = h;

  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(
    75,
    window.innerWidth / window.innerHeight,
    0.1,
    100000
  );

  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  document.body.appendChild(renderer.domElement);

  universe.attachToScene(scene, camera);

  window.addEventListener("resize", () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });
}

export function renderLoop() {
  requestAnimationFrame(renderLoop);

  const now = performance.now();
  const dt = (now - last) / 1000;
  last = now;

  updateTime(dt, () => universe.onYear());

  universe.update();
  hud.update();
  renderer.render(scene, camera);
}
EOF

# ----------------------------
# core/input.js
# ----------------------------
cat > core/input.js <<'EOF'
export function initInput(universe) {
  const keys = {};

  window.addEventListener("keydown", e => keys[e.key.toLowerCase()] = true);
  window.addEventListener("keyup", e => keys[e.key.toLowerCase()] = false);

  universe.bindControls(() => ({
    thrust: keys["w"],
    brake: keys["s"],
    yawL: keys["a"],
    yawR: keys["d"],
    pitchU: keys["r"],
    pitchD: keys["f"],
    select: keys[" "],
    land: keys["l"]
  }));
}
EOF

# ----------------------------
# core/time.js
# ----------------------------
cat > core/time.js <<'EOF'
export const YEAR_SECONDS = 10;
let accumulator = 0;

export function updateTime(dt, onYear) {
  accumulator += dt;
  if (accumulator >= YEAR_SECONDS) {
    accumulator = 0;
    onYear();
  }
}
EOF

# ----------------------------
# world/universe.js
# ----------------------------
cat > world/universe.js <<'EOF'
import { StarSystem } from "./system.js";
import { LandingController } from "../gameplay/landing.js";
import { yearlyProduction } from "../systems/production.js";
import { terraformStep } from "../systems/terraforming.js";

export class Universe {
  constructor() {
    this.systems = [ new StarSystem() ];
    this.activeSystem = this.systems[0];
    this.controls = null;
    this.camera = null;
    this.landing = null;
  }

  attachToScene(scene, camera) {
    this.camera = camera;
    this.landing = new LandingController(camera);
    camera.position.z = 5000;
    this.activeSystem.attach(scene);
  }

  bindControls(fn) {
    this.controls = fn;
  }

  update() {
    if (!this.controls) return;
    this.landing.update();
    if (this.landing.state === "flying") {
      this.activeSystem.update(this.controls(), this.camera, this.landing);
    }
  }

  onYear() {
    const race = window.__race;
    this.activeSystem.planets.forEach(p => {
      p.grow(race);
      terraformStep(p, race);
      yearlyProduction(p, race);
    });
  }
}
EOF

# ----------------------------
# world/system.js
# ----------------------------
cat > world/system.js <<'EOF'
import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.160/build/three.module.js";
import { Planet } from "./planet.js";
import { createScannerRing } from "../gameplay/scanning.js";

export class StarSystem {
  constructor() {
    this.star = new THREE.Mesh(
      new THREE.SphereGeometry(300, 32, 32),
      new THREE.MeshBasicMaterial({ color: 0xffffaa })
    );

    this.planets = [
      new Planet("Astra", 1200),
      new Planet("Boreas", 2200),
      new Planet("Cinder", 3600)
    ];

    this.scanner = createScannerRing(3000);
  }

  attach(scene) {
    scene.add(this.star);
    scene.add(this.scanner);
    this.planets.forEach(p => p.attach(scene));
  }

  update(ctrl, camera, landing) {
    if (ctrl.thrust) camera.translateZ(-20);
    if (ctrl.brake) camera.translateZ(20);
    if (ctrl.yawL) camera.rotation.y += 0.01;
    if (ctrl.yawR) camera.rotation.y -= 0.01;

    this.planets.forEach(p => {
      const d = camera.position.distanceTo(p.mesh.position);
      if (d < 600 && ctrl.select) {
        landing.enterOrbit(p);
        window.__selectedPlanet = p;
        window.__landingState = "orbiting";
      }
      p.update();
    });

    if (ctrl.land && window.__selectedPlanet) {
      landing.land();
      window.__landingState = "landed";
      window.__selectedPlanet.colonize();
    }
  }
}
EOF

# ----------------------------
# world/planet.js
# ----------------------------
cat > world/planet.js <<'EOF'
import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.160/build/three.module.js";
import { habitabilityScore } from "../systems/habitability.js";

export class Planet {
  constructor(name, orbit) {
    this.name = name;
    this.orbit = orbit;

    this.env = {
      gravity: Math.random() * 2,
      temp: Math.random() * 200 - 50,
      rad: Math.random() * 100
    };

    this.minerals = {
      ironium: { surface: 100000 },
      boranium: { surface: 80000 },
      germanium: { surface: 60000 }
    };

    this.population = 0;
    this.resources = 0;
    this.installations = { factories: 0, mines: 0, defenses: 0 };

    this.mesh = new THREE.Mesh(
      new THREE.SphereGeometry(120, 24, 24),
      new THREE.MeshBasicMaterial({ color: 0x4444ff })
    );
    this.mesh.position.x = orbit;
  }

  attach(scene) {
    scene.add(this.mesh);
  }

  update() {
    this.mesh.rotation.y += 0.002;
  }

  colonize(initial = 10000) {
    if (this.population === 0) this.population = initial;
  }

  grow(race) {
    if (this.population <= 0) return;
    const h = habitabilityScore(this.env, race);
    const rate = 0.15 * h * race.modifiers.growth;
    this.population = Math.floor(this.population * (1 + rate));
  }

  getMetrics(race) {
    return {
      habitability: habitabilityScore(this.env, race),
      env: this.env,
      minerals: this.minerals
    };
  }
}
EOF

# ----------------------------
# gameplay/landing.js
# ----------------------------
cat > gameplay/landing.js <<'EOF'
export const LandingState = {
  FLYING: "flying",
  ORBITING: "orbiting",
  LANDED: "landed"
};

export class LandingController {
  constructor(camera) {
    this.camera = camera;
    this.state = LandingState.FLYING;
    this.targetPlanet = null;
  }

  enterOrbit(planet) {
    this.state = LandingState.ORBITING;
    this.targetPlanet = planet;
  }

  land() {
    this.state = LandingState.LANDED;
  }

  update() {
    if (this.state === LandingState.ORBITING && this.targetPlanet) {
      const p = this.targetPlanet.mesh.position;
      this.camera.lookAt(p);
    }
  }
}
EOF

# ----------------------------
# gameplay/scanning.js
# ----------------------------
cat > gameplay/scanning.js <<'EOF'
import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.160/build/three.module.js";

export function createScannerRing(range, color = 0x00ff00) {
  const geom = new THREE.RingGeometry(range - 5, range, 64);
  const mat = new THREE.MeshBasicMaterial({
    color,
    side: THREE.DoubleSide,
    transparent: true,
    opacity: 0.15
  });
  const ring = new THREE.Mesh(geom, mat);
  ring.rotation.x = Math.PI / 2;
  return ring;
}
EOF

# ----------------------------
# systems/*
# ----------------------------
cat > systems/habitability.js <<'EOF'
export function habitabilityScore(env, race) {
  function s(v, i, r) {
    return Math.max(0, 1 - Math.abs(v - i) / r);
  }
  return s(env.gravity, race.ideal.gravity, race.range.gravity) *
         s(env.temp, race.ideal.temp, race.range.temp) *
         s(env.rad, race.ideal.rad, race.range.rad);
}
EOF

cat > systems/production.js <<'EOF'
export function yearlyProduction(p, race) {
  if (p.population <= 0) return;

  const maxF = Math.floor((p.population / 10000) * 10);
  const maxM = Math.floor((p.population / 10000) * 10);

  p.installations.factories = Math.min(p.installations.factories, maxF);
  p.installations.mines = Math.min(p.installations.mines, maxM);

  p.resources += Math.floor(p.population / 1000);
}
EOF

cat > systems/terraforming.js <<'EOF'
export function terraformStep(p, race) {
  const r = race.modifiers.terraforming || 0;
  function shift(v, i, s) {
    return v < i ? Math.min(v + s, i) : Math.max(v - s, i);
  }
  p.env.gravity = shift(p.env.gravity, race.ideal.gravity, 0.01 * r);
  p.env.temp = shift(p.env.temp, race.ideal.temp, 0.5 * r);
  p.env.rad = shift(p.env.rad, race.ideal.rad, 0.5 * r);
}
EOF

cat > systems/traits.js <<'EOF'
export const CLAIM_ADJUSTER = {
  name: "Claim Adjuster",
  ideal: { gravity: 1, temp: 20, rad: 5 },
  range: { gravity: 0.6, temp: 40, rad: 15 },
  modifiers: { growth: 1.0, terraforming: 2.0 }
};
EOF

# ----------------------------
# ui/hud.js
# ----------------------------
cat > ui/hud.js <<'EOF'
export class HUD {
  constructor(universe) {
    this.el = document.createElement("pre");
    this.el.style.position = "fixed";
    this.el.style.bottom = "10px";
    this.el.style.left = "10px";
    this.el.style.color = "#0f0";
    document.body.appendChild(this.el);
  }

  update() {
    const p = window.__selectedPlanet;
    if (!p) {
      this.el.textContent = "FLYING";
      return;
    }
    const m = p.getMetrics(window.__race);
    this.el.textContent =
`PLANET ${p.name}
Habitability ${(m.habitability*100).toFixed(1)}%
Population ${p.population}
Resources ${p.resources}`;
  }
}
EOF

echo "Done. Open index.html via a local server."

