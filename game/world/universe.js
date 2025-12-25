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
