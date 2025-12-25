export function createControls() {
  const ctrl = {
    thrust: false,
    brake: false,
    yawL: false,
    yawR: false,
    select: false,
    land: false,
    escape: false
  };

  window.addEventListener("keydown", e => {
    switch (e.code) {
      case "KeyW": ctrl.thrust = true; break;
      case "KeyS": ctrl.brake = true; break;
      case "KeyA": ctrl.yawL = true; break;
      case "KeyD": ctrl.yawR = true; break;
      case "Space": ctrl.select = true; break;
      case "KeyL": ctrl.land = true; break;
      case "Escape": ctrl.escape = true; break;
    }
  });

  window.addEventListener("keyup", e => {
    switch (e.code) {
      case "KeyW": ctrl.thrust = false; break;
      case "KeyS": ctrl.brake = false; break;
      case "KeyA": ctrl.yawL = false; break;
      case "KeyD": ctrl.yawR = false; break;
      case "Space": ctrl.select = false; break;
      case "KeyL": ctrl.land = false; break;
      case "Escape": ctrl.escape = false; break;
    }
  });

  return ctrl;
}

