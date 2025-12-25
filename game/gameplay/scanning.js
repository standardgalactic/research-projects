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
