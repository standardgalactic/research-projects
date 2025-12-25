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
