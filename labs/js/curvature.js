// curvature.js – Lab 01: simple 2D curvature field demo

(function () {
  const canvas = document.getElementById('curvCanvas');
  const ctx = canvas.getContext('2d');
  const N = 32; // grid resolution
  const cell = canvas.width / N;

  const curvSlider = document.getElementById('curvSlider');
  const dampSlider = document.getElementById('dampSlider');
  const curvValue = document.getElementById('curvValue');
  const dampValue = document.getElementById('dampValue');
  const resetBtn = document.getElementById('resetBtn');
  const kickBtn = document.getElementById('kickBtn');

  let k = 0.03;
  let damping = 0.9;

  let x = 0, y = 0;
  let vx = 0, vy = 0;

  function reset() {
    x = (Math.random() - 0.5) * 3;
    y = (Math.random() - 0.5) * 3;
    vx = vy = 0;
  }

  function kick() {
    vx += (Math.random() - 0.5) * 1.5;
    vy += (Math.random() - 0.5) * 1.5;
  }

  reset();

  curvSlider.addEventListener('input', () => {
    const val = parseInt(curvSlider.value, 10);
    k = val / 100; // 0.01 - 1.0
    curvValue.textContent = k.toFixed(2);
  });

  dampSlider.addEventListener('input', () => {
    const val = parseInt(dampSlider.value, 10);
    damping = val / 100; // 0.7 - 0.99
    dampValue.textContent = damping.toFixed(2);
  });

  resetBtn.addEventListener('click', reset);
  kickBtn.addEventListener('click', kick);

  function potential(px, py) {
    return k * (px * px + py * py);
  }

  function grad(px, py) {
    // gradient of k(x^2 + y^2) is (2k x, 2k y)
    return [2 * k * px, 2 * k * py];
  }

  function worldToGrid(px, py) {
    // map [-3, 3] to [0, N)
    const gx = Math.max(0, Math.min(N - 1, Math.floor((px + 3) / 6 * N)));
    const gy = Math.max(0, Math.min(N - 1, Math.floor((py + 3) / 6 * N)));
    return [gx, gy];
  }

  function drawField() {
    for (let i = 0; i < N; i++) {
      for (let j = 0; j < N; j++) {
        const px = (i / (N - 1)) * 6 - 3;
        const py = (j / (N - 1)) * 6 - 3;
        const V = potential(px, py);
        const maxV = k * 18; // approx at radius ~3
        const t = Math.min(1, V / maxV);
        const c = Math.floor((1 - t) * 255);
        ctx.fillStyle = `rgb(0, ${c}, 60)`;
        ctx.fillRect(i * cell, j * cell, cell, cell);
      }
    }
  }

  function drawParticle() {
    const [gx, gy] = worldToGrid(x, y);
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(gx * cell, gy * cell, cell, cell);
  }

  function step() {
    // gradient descent dynamics with damping
    const [gx, gy] = grad(x, y);
    vx -= gx * 0.05;
    vy -= gy * 0.05;

    vx *= damping;
    vy *= damping;

    x += vx * 0.05;
    y += vy * 0.05;

    // keep within bounds
    x = Math.max(-3, Math.min(3, x));
    y = Math.max(-3, Math.min(3, y));
  }

  function loop() {
    step();
    drawField();
    drawParticle();
    requestAnimationFrame(loop);
  }

  drawField();
  drawParticle();
  requestAnimationFrame(loop);
})();
