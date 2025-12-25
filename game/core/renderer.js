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
