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
