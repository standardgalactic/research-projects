export function initInput(universe) {
  const keys = {};

  window.addEventListener("keydown", e => {
    keys[e.key.toLowerCase()] = true;
  });

  window.addEventListener("keyup", e => {
    keys[e.key.toLowerCase()] = false;
  });

  universe.bindControls(() => ({
    thrust: keys["w"],
    brake: keys["s"],
    yawL: keys["a"],
    yawR: keys["d"],
    pitchU: keys["r"],
    pitchD: keys["f"],
    select: keys[" "],        // Spacebar
    land: keys["l"],
    escape: keys["escape"]    // ✅ THIS IS THE MISSING LINE
  }));
}
