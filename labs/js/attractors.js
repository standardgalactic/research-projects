// attractors.js – Lab 04: Double-well attractor switching

(function () {
  const canvas = document.getElementById('attCanvas');
  const ctx = canvas.getContext('2d');

  const bhSlider = document.getElementById('bhSlider');
  const nsSlider = document.getElementById('nsSlider');
  const bhVal = document.getElementById('bhVal');
  const nsVal = document.getElementById('nsVal');
  const resetXBtn = document.getElementById('resetXBtn');

  let barrier = 1.0;
  let noise = 0.2;
  let x = -1;
  let t = 0;
  const maxT = 360;

  function updateParams() {
    barrier = parseInt(bhSlider.value, 10) / 100;
    noise = parseInt(nsSlider.value, 10) / 100;
    bhVal.textContent = barrier.toFixed(2);
    nsVal.textContent = noise.toFixed(2);
  }

  bhSlider.addEventListener('input', updateParams);
  nsSlider.addEventListener('input', updateParams);

  resetXBtn.addEventListener('click', () => {
    x = (Math.random() < 0.5 ? -1 : 1);
    t = 0;
    clearCanvas();
  });

  updateParams();

  function clearCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = '#33ff99';
    ctx.strokeRect(0, 0, canvas.width, canvas.height);
  }

  clearCanvas();

  function potentialGradient(x) {
    // Simple double-well: V(x) = (x^2 - 1)^2 * barrier
    // dV/dx = 4x(x^2 - 1) * barrier
    return 4 * x * (x * x - 1) * barrier;
  }

  function step() {
    const grad = potentialGradient(x);
    const dt = 0.02;
    const deterministic = -grad * dt;
    const stochastic = noise * (Math.random() - 0.5);
    x += deterministic + stochastic;

    if (x < -2) x = -2;
    if (x > 2) x = 2;

    t += 1;
    if (t > maxT) {
      t = 0;
      clearCanvas();
    }
  }

  function draw() {
    const xNorm = (x + 2) / 4;
    const y = canvas.height - (xNorm * (canvas.height - 4)) - 2;
    const xPix = (t / maxT) * canvas.width;
    ctx.fillStyle = '#66ffcc';
    ctx.fillRect(xPix, y, 2, 2);
  }

  function loop() {
    step();
    draw();
    requestAnimationFrame(loop);
  }

  requestAnimationFrame(loop);
})();
