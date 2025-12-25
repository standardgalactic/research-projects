import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.160/build/three.module.js";
import { habitabilityScore } from "../systems/habitability.js";

export class Planet {
  constructor(name, orbit) {
    this.name = name;
    this.orbit = orbit;

    this.defaultColor = 0x4466ff;
    this.highlightColor = 0xffff00;


    // -------------------------
    // Environment
    // -------------------------
    this.env = {
      gravity: +(Math.random() * 2).toFixed(2),
      temp: +(Math.random() * 200 - 50).toFixed(1),
      rad: +(Math.random() * 100).toFixed(1)
    };

    // -------------------------
    // Minerals
    // -------------------------
    this.minerals = {
      ironium: { conc: randConc(), surface: 100000 },
      boranium: { conc: randConc(), surface: 80000 },
      germanium: { conc: randConc(), surface: 60000 }
    };

    // -------------------------
    // Economy
    // -------------------------
    this.population = 0;
    this.resources = 0;

    this.installations = {
      factories: 0,
      mines: 0,
      defenses: 0
    };

    // -------------------------
    // Build queue (Stars!-style)
    // -------------------------
    this.buildQueue = {
      factories: 0,
      mines: 0,
      terraform: false
    };

    // -------------------------
    // Visual
    // -------------------------
    this.mesh = new THREE.Mesh(
      new THREE.SphereGeometry(120, 24, 24),
      new THREE.MeshBasicMaterial({ color: this.defaultColor })
  );

    this.mesh.position.x = orbit;
  }

  attach(scene) {
    scene.add(this.mesh);
  }

  update() {
    this.mesh.rotation.y += 0.002;
  }

setHighlighted(on) {
  this.mesh.material.color.setHex(
    on ? this.highlightColor : this.defaultColor
  );
}




  // =========================
  // COLONIZATION
  // =========================
  colonize(initial = 10000) {
    if (this.population > 0) return;
    this.population = initial;
  }

  // =========================
  // POPULATION DYNAMICS
  // =========================
  maxPopulation(race) {
    return Math.floor(1_000_000 * habitabilityScore(this.env, race));
  }

  grow(race) {
    if (this.population <= 0) return;

    const h = habitabilityScore(this.env, race);
    const cap = this.maxPopulation(race);

    if (h <= 0) {
      this.population = Math.floor(this.population * 0.8);
      return;
    }

    const crowd = Math.min(1, this.population / cap);
    const rate = 0.15 * h * race.modifiers.growth * (1 - crowd);

    this.population = Math.floor(this.population * (1 + rate));
    if (this.population > cap) this.population = Math.floor(cap * 0.95);
  }

  // =========================
  // BUILD PHASE (per year)
  // =========================
  applyBuildQueue() {
    let r = this.resources;

    // factories cost 10
    while (this.buildQueue.factories > 0 && r >= 10) {
      this.installations.factories++;
      this.buildQueue.factories--;
      r -= 10;
    }

    // mines cost 10
    while (this.buildQueue.mines > 0 && r >= 10) {
      this.installations.mines++;
      this.buildQueue.mines--;
      r -= 10;
    }

    this.resources = r;
  }

  // =========================
  // TERRAFORMING (flag-based)
  // =========================
  terraformStep(race) {
    if (!this.buildQueue.terraform) return;

    function shift(v, i, s) {
      if (v < i) return Math.min(v + s, i);
      if (v > i) return Math.max(v - s, i);
      return v;
    }

    const rate = race.modifiers.terraforming || 0;

    this.env.gravity = shift(this.env.gravity, race.ideal.gravity, 0.01 * rate);
    this.env.temp = shift(this.env.temp, race.ideal.temp, 0.5 * rate);
    this.env.rad = shift(this.env.rad, race.ideal.rad, 0.5 * rate);
  }

  // =========================
  // METRICS
  // =========================
  habitabilityClass(race) {
    const h = habitabilityScore(this.env, race);
    if (h >= 0.33) return "1:3";
    if (h >= 0.2) return "1:5";
    if (h >= 0.1) return "1:9";
    return "Hostile";
  }

  getMetrics(race) {
    const h = habitabilityScore(this.env, race);
    return {
      habitability: h,
      class: this.habitabilityClass(race),
      maxPop: this.maxPopulation(race),
      population: this.population,
      resources: this.resources,
      env: this.env,
      minerals: this.minerals,
      installations: this.installations,
      queue: this.buildQueue
    };
  }
}

function randConc() {
  return Math.floor(30 + Math.random() * 70);
}
