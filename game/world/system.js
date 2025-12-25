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
    // ----------------------------
    // Ship movement (unchanged)
    // ----------------------------
    if (ctrl.thrust) camera.translateZ(-20);
    if (ctrl.brake) camera.translateZ(20);
    if (ctrl.yawL) camera.rotation.y += 0.01;
    if (ctrl.yawR) camera.rotation.y -= 0.01;

    // ----------------------------
    // Planet targeting logic
    // ----------------------------
    let closestPlanet = null;
    let closestDist = Infinity;

    for (const p of this.planets) {
      const d = camera.position.distanceTo(p.mesh.position);

      // clear highlight by default
      if (p.setHighlighted) p.setHighlighted(false);

      if (d < 800 && d < closestDist) {
        closestPlanet = p;
        closestDist = d;
      }

      p.update();
    }

    // ----------------------------
    // Highlight + select
    // ----------------------------
    if (closestPlanet) {
      if (closestPlanet.setHighlighted) {
        closestPlanet.setHighlighted(true);
      }

      // Space confirms selection
      if (ctrl.select) {
        landing.enterOrbit(closestPlanet);
        window.__selectedPlanet = closestPlanet;
        window.__landingState = "orbiting";
      }
    }

    // ----------------------------
    // Landing
    // ----------------------------
    if (ctrl.land && window.__selectedPlanet) {
      landing.land();
      window.__landingState = "landed";
      window.__selectedPlanet.colonize();
    }
  }
}
